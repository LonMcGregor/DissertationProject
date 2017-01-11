from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import student.models as m
import student.permission as p
import student.forms as f


@login_required()
def index(request):
    return render(request, 'student/index.html')


@login_required()
@p.cw_exists_for_upload
def upload_solution(request, singlecw=None):
    """Given an @request@, generate and handle an upload form
    for the specified coursework @singlecw@. If there is a
    POST form attached, upload the desired file."""
    if singlecw is None or singlecw == "":
        return Http404()
    cw = m.Coursework.objects.get(id=singlecw)
    if request.method == 'POST':
        upload = f.FileUploadForm(request.POST, request.FILES)
        if not upload.is_valid():
            return HttpResponseForbidden()
        if not p.user_can_upload_of_type(request.user, cw, upload.cleaned_data['file_type']):
            return HttpResponseForbidden()

        s = m.File(coursework=cw, creator=request.user,
                   filepath=upload.cleaned_data['chosen_file'],
                   type=upload.cleaned_data['file_type'])
        s.save()

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
    """For a given @file, return the file path,
    or empty string is file doesnt exist"""
    if file is not None:
        return file.filepath
    return ""


def single_coursework(request, coursework):
    cw = m.Coursework.objects.get(id=coursework)
    if not p.can_view_coursework(request.user, cw):
        return HttpResponseForbidden()
    sol = p.user_submitted_solution(request.user, cw)
    test = p.user_test_case(request.user, cw)
    result = p.user_test_result(test)
    if result is not None:
        waiting = result.waiting_to_run
        feedback = result.feedback
        results = result.results
    else:
        waiting = False
        feedback = None
        results = None
    own_feedback = p.user_feedback_for_solution(sol)
    details = {
        "cw": cw,
        "has_submitted_solution": sol is not None,
        "solution_url": path_for_file(sol),
        "has_submitted_test": test is not None,
        "test_url": path_for_file(test),
        "waiting_on_test": waiting,
        "test_results_url": path_for_file(results),
        "has_given_feedback": feedback is not None,
        "feedback_results_url": path_for_file(feedback),
        "has_own_feedback": own_feedback is not None,
        "own_feedback_results_url": path_for_file(own_feedback),
    }
    return render(request, 'student/detail_coursework.html', details)
