from django.core.files.base import ContentFile
from django.http import Http404, HttpResponseForbidden, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import student.models as m
import student.permission as p
import student.forms as f
import student.runner as r
from django.db import transaction
from pygments import highlight as pyghi
from pygments.lexers import python as pyglex
from pygments.formatters import html as pygform


@login_required()
def index(request):
    return render(request, 'student/index.html')


@login_required()
@p.cw_exists_for_upload
@transaction.atomic
def upload_solution(request, singlecw=None):
    """Given an @request@, generate and handle an upload form
    for the specified coursework @singlecw@. If there is a
    POST form attached, upload the desired file."""
    if singlecw is None or singlecw == "":
        return Http404()
    cw = m.Coursework.objects.get(id=singlecw)
    user = request.user
    if request.method == 'POST':
        upload = f.FileUploadForm(request.POST, request.FILES)
        if not upload.is_valid():
            return HttpResponseForbidden()
        if not p.user_can_upload_of_type(user, cw, upload.cleaned_data['file_type']):
            return HttpResponseForbidden()
        file_type = upload.cleaned_data['file_type']
        submission = m.File(coursework=cw, creator=user,
                            filepath=upload.cleaned_data['chosen_file'],
                            type=file_type)
        submission.save()

        if file_type in [m.FileType.TEST_CASE, m.FileType.SOLUTION]:
            r.new_item_uploaded(user, cw, submission, file_type)
            # r.run_queued_tests()
            # todo make this run test happen async and notify @initiator when complete

        msg = "Upload of %s was completed" % request.FILES['chosen_file'],
        allow_upload = False
    else:
        state = p.state_of_user_in_coursework(request.user, cw)
        if state == p.UserCourseworkState.SOLUTION:
            msg = "You need to upload a solution for this coursework"
            allow_upload = True
        elif state == p.UserCourseworkState.TESTCASE:
            msg = "You need to upload a test case for this coursework"
            allow_upload = True
        elif state == p.UserCourseworkState.TESTWAIT:
            msg = "Please wait for your test case to be run and results collected"
            allow_upload = False
        elif state == p.UserCourseworkState.FEEDBACK:
            msg = "Please provide feedback for test results"
            allow_upload = True
        elif state == p.UserCourseworkState.COMPLETE:
            msg = "You have completed this coursework"
            allow_upload = False
        else:
            return HttpResponseForbidden()

    detail = {
        "ff": f.FileUploadForm,
        "allow_upload": allow_upload,
        "msg": msg
    }
    return render(request, 'student/upload_solution.html', detail)


@login_required()
def upload_test(request, singlecw):
    if singlecw is None or singlecw == "":
        return Http404()
    if not p.can_view_coursework(request.user, singlecw):
        return HttpResponseForbidden()


def retrieve_coursework(request):
    """For a given @request, return a list of courseworks available to the user"""
    logged_in_user = request.user
    enrolled_courses = m.EnrolledUser.objects.filter(login=logged_in_user).values('course')
    courses_for_user = m.Course.objects.filter(id__in=enrolled_courses)
    all_courseworks_for_user = m.Coursework.objects.filter(course__in=courses_for_user)
    visible_courseworks = []
    for item in all_courseworks_for_user:
        if p.can_view_coursework(logged_in_user, item):
            visible_courseworks.append((item.id, item.state, item.course.code, item.name))
    return visible_courseworks


@login_required()
def detail_coursework(request, singlecw=None):
    if singlecw is None or singlecw == "":
        available = retrieve_coursework(request)
        return render(request, 'student/choose_coursework.html', {'courseworks': available})
    return single_coursework(request, singlecw)


def path_for_file(file):
    """For a given @file, return the file id,
    or empty string is file doesnt exist"""
    if file is not None:
        return file.id
    return ""


def get_test_data(user, coursework):
    """Get the test data for the tester @user, within a given @coursework"""
    # todo currently this all acts assuming a test case is made once per cw
    test_results = m.TestData.objects.filter(initiator=user, coursework=coursework)
    if test_results.count() > 0:
        return test_results[0]
    return None


def get_feedback_for_solution(coursework, solution):
    """Get the feedback for the developer, based on a @coursework for a @solution"""
    # todo assumes someone will only get one feedback per coursework
    test_results = m.TestData.objects.filter(coursework=coursework, solution=solution)
    if test_results.count() > 0:
        return test_results[0].feedback
    return None


def single_coursework(request, coursework):
    cw = m.Coursework.objects.get(id=coursework)
    if not p.can_view_coursework(request.user, cw):
        return HttpResponseForbidden()
    sol = p.user_submitted_solution(request.user, cw)
    test = p.user_test_case(request.user, cw)
    result = get_test_data(request.user, coursework)
    if result is not None:
        waiting = result.waiting_to_run
        given_feedback = result.feedback
        results = result.results
    else:
        waiting = False
        given_feedback = None
        results = None
    own_feedback = get_feedback_for_solution(coursework, sol)
    details = {
        "cw": cw,
        "has_submitted_solution": sol is not None,
        "solution_url": path_for_file(sol),
        "has_submitted_test": test is not None,
        "test_url": path_for_file(test),
        "waiting_on_test": waiting,
        "test_results_url": path_for_file(results),
        "has_given_feedback": given_feedback is not None,
        "feedback_results_url": path_for_file(given_feedback),
        "has_own_feedback": own_feedback is not None,
        "own_feedback_results_url": path_for_file(own_feedback),
    }
    return render(request, 'student/detail_coursework.html', details)


@login_required()
def feedback(request, test_data):
    # todo right now this assumes that the user only submits and runs one test_data per coursework
    test_data_instance = m.TestData.objects.get(coursework=test_data, initiator=request.user)
    # test_data_instance = m.TestData.objects.get(id=test_data)
    perm = p.user_feedback_mode(request.user, test_data_instance)
    if perm == p.UserFeedbackModes.DENY:
        return HttpResponseForbidden()
    if perm == p.UserFeedbackModes.WAIT:
        return HttpResponse("Please wait until the test has finished running")
    if request.POST:
        feedback_upload(request, perm, test_data_instance)
        perm = p.UserFeedbackModes.READ
    details = {
        "test_data": test_data_instance,
        "can_submit": perm == p.UserFeedbackModes.WRITE
    }
    return render(request, 'student/feedback.html', details)


@transaction.atomic()
def feedback_upload(request, perm, test_data_instance):
    if perm != p.UserFeedbackModes.WRITE:
        return HttpResponseForbidden()
    feedback_text = request.POST["feedback"]
    feedback_file = m.File(coursework=test_data_instance.coursework, creator=request.user,
                           type=m.FileType.FEEDBACK)
    feedback_file.filepath.save('feedback.txt', ContentFile(feedback_text))
    feedback_file.save()
    test_data_instance.feedback = feedback_file
    test_data_instance.save()


@login_required()
def show_file(request, file_id):
    # todo may want permission mixin - make it so only creator, tester or teacher can view
    file = m.File.objects.get(id=file_id)
    if not p.can_view_file(request.user, file):
        return HttpResponseForbidden()
    content = read_file_by_line(file.filepath)
    return HttpResponse(content_type="text/plain", charset="utf-8", content=content)


@login_required()
def render_file(request, file_id):
    file = m.File.objects.get(id=file_id)
    if not p.can_view_file(request.user, file):
        return HttpResponseForbidden()
    content = read_file_by_line(file.filepath)
    detail = {
        "content": pyghi(content, pyglex.PythonLexer(), pygform.HtmlFormatter())
    }
    return render(request, 'student/pretty_file.html', detail)


def read_file_by_line(file):
    content = ""
    while True:
        buf = file.readline()
        content += buf.decode('utf-8')
        if buf == b'':
            return content
