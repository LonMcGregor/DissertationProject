from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import Http404, HttpResponseForbidden, HttpResponse
from django.http.response import FileResponse
from django.shortcuts import render
from pygments import highlight as pyghi
from pygments.formatters import html as pygform
from pygments.lexers import python as pyglex

from runner import matcher
import runner.runner as r
import student.forms as f
import student.helper as h
import student.models as m
import student.permission as p


@login_required()
def index(request):
    return detail_coursework(request)


@login_required()
@transaction.atomic
def upload_solution(request, cw=None):
    """Given an @request@, generate and handle an upload form
    for the specified coursework @cw. If there is a
    POST form attached, upload the desired file."""
    no_cws = m.Coursework.objects.filter(id=cw).count() != 1
    if cw is None or cw == "" or no_cws:
        return Http404("No coursework has been specified")
    cw_instance = m.Coursework.objects.get(id=cw)
    if not p.can_view_coursework(request.user, cw_instance):
        return HttpResponseForbidden("You are not allowed to see this coursework")
    if cw_instance.state != m.CourseworkState.UPLOAD:
        return HttpResponseForbidden("This coursework is not currently accepting uploads")
    state = p.state_of_user_in_coursework(request.user, cw_instance)
    msg, allow_upload, error = upload_solution_render(state)
    if error:
        return error
    if request.method == 'POST':
        result = upload_solution_post(request, cw_instance)
        if result:
            return result
        msg = "Upload of files was completed",
        allow_upload = False
    detail = {
        "allow_upload": allow_upload,
        "msg": msg,
        "crumbs": [("Homepage", "/student"), ("Coursework", "/student/cw/%s" % cw)]
    }
    return render(request, 'student/upload_solution.html', detail)


def upload_solution_post(request, cw_instance):
    """Handles the POST request of the upload, and
    saves the file to the system / database. Also
    starts the job of making / running test data
    instances. Returns either an Http error code
    or False, if no error has occurred."""
    user = request.user
    data = request.POST
    if not p.user_can_upload_of_type(user, cw_instance, data['file_type']):
        return HttpResponseForbidden("You can't upload submissions of this type")
    file_type = data['file_type']
    is_private = 'keep_private' in data
    submission = m.Submission(id=m.new_random_slug(m.Submission), coursework=cw_instance,
                              creator=user, type=file_type,
                              private=is_private)
    submission.save()
    for each in request.FILES.getlist('chosen_files'):
        m.File(file=each, submission=submission).save()
    return False


def upload_solution_render(state):
    """For a given @state,  determine
    what message to show on the upload page, and if
    an upload should be allowed at this stage.
    Return the message, allowed, and any errors"""
    if state == p.UserCourseworkState.UPLOADS:
        msg = "Please upload a solution for this coursework"
        allow_upload = True
    elif state == p.UserCourseworkState.FEEDBACK:
        msg = "You may now use the feedback view to submit feedback. Please visit the coursework " \
              "detail page for more information."
        allow_upload = True
    elif state == p.UserCourseworkState.COMPLETE:
        msg = "The deadline for submissions for this coursework has passed"
        allow_upload = False
    elif state == p.UserCourseworkState.NOACCESS:
        msg = "You are not allowed to upload files for this coursework"
        allow_upload = False
    else:
        return None, None, HttpResponseForbidden("Invalid coursework state")
    return msg, allow_upload, False


@login_required()
def detail_coursework(request, cw=None):
    """If a coursework @cw is specified,return the page detailing it
    otherwise return a listing of all currently available tasks. """
    if cw is None or cw == "":
        available = retrieve_coursework(request)
        return render(request, 'student/choose_coursework.html', {'courseworks': available})
    return single_coursework(request, cw)


def single_coursework(request, coursework):
    cw = m.Coursework.objects.get(id=coursework)
    if not p.can_view_coursework(request.user, cw):
        return HttpResponseForbidden("You are not allowed to access this coursework")

    descriptors = [(s, h.get_files(s)) for s in m.Submission.objects.filter(
        type=m.SubmissionType.CW_DESCRIPTOR, coursework=coursework)]
    solutions = [(s, h.get_files(s)) for s in m.Submission.objects.filter(
        coursework=coursework, creator=request.user, type=m.SubmissionType.SOLUTION)]
    tests = [(t, h.get_files(t)) for t in m.Submission.objects.filter(
        coursework=coursework, creator=request.user, type=m.SubmissionType.TEST_CASE)]

    initiated = h.get_test_match_for_developing(request.user, coursework)
    marking = m.TestMatch.objects.filter(coursework=coursework, marker=request.user)
    developed = h.get_test_match_for_developer(request.user, coursework)

    details = {
        "cw": cw,
        "tm_form": f.TestMatchForm(),
        "descriptors": descriptors,
        "solutions": solutions,
        "tests": tests,
        "initiated": initiated,
        "marking": marking,
        "developed": developed,
        "subs_open": cw.state == m.CourseworkState.UPLOAD,
        "feedback_open": cw.state == m.CourseworkState.FEEDBACK,
        "crumbs": [("Homepage", "/student")]
    }
    return render(request, 'student/detail_coursework.html', details)


@login_required()
def create_test_match(request, cw):
    """Recieve a POST request to create a student test match"""
    if not request.POST:
        return HttpResponseForbidden("You're supposed to POST a form here")
    tm_form = f.TestMatchForm(request.POST)
    if not tm_form.is_valid():
        return HttpResponseForbidden("Invalid form data")
    try:
        new_tm = matcher.student_create_single_test_match(
            tm_form.cleaned_data['solution'],
            tm_form.cleaned_data['test'],
            cw,
            request.user
        )
        r.run_test_on_thread(new_tm, r.execute_python3_unit)
    except Exception as e:
        return HttpResponseForbidden(str(e))
    return HttpResponse("Test has been created")


def retrieve_coursework(request):
    """For a given @request, return a list of coursework available to the user"""
    logged_in_user = request.user
    enrolled_courses = m.EnrolledUser.objects.filter(login=logged_in_user).values('course')
    courses_for_user = m.Course.objects.filter(code__in=enrolled_courses)
    all_courseworks_for_user = m.Coursework.objects.filter(course__in=courses_for_user)
    visible_courseworks = []
    for item in all_courseworks_for_user:
        if p.can_view_coursework(logged_in_user, item):
            visible_courseworks.append((item.id, item.state, item.course.code, item.name))
    return visible_courseworks


@login_required()
def feedback(request, test_match):
    """Render the page that allows a user to give feedback to a certain
    test data instance. Also handle the case of POST data upload."""
    test_match_instance = m.TestMatch.objects.get(id=test_match)
    perm = p.user_feedback_mode(request.user, test_match_instance)
    if perm == p.UserFeedbackModes.DENY:
        return HttpResponseForbidden("You are not allowed to see this test data")
    if perm == p.UserFeedbackModes.WAIT:
        return HttpResponse("Please wait until the test has finished running")
    if request.POST:
        if perm != p.UserFeedbackModes.WRITE:
            return HttpResponseForbidden("You are not allowed to submit feedback")
        feedback_upload(request, test_match_instance)
        return HttpResponse("Your feedback has been recorded")
    feedback_files = h.get_files(test_match_instance.feedback)
    details = {
        "test_match": test_match_instance,
        "can_submit": perm == p.UserFeedbackModes.WRITE,
        "test_files": h.get_files(test_match_instance.test)[0],
        "result_files": h.get_files(test_match_instance.result)[0],
        "solution_files": h.get_files(test_match_instance.solution)[0],
        "feedback_files": feedback_files[0] if len(feedback_files) > 0 else None,
        # todo for now, assume only 1 files
        "crumbs": [("Homepage", "/student"),
                   ("Coursework", "/student/cw/%s" % test_match_instance.coursework.id)]
    }
    return render(request, 'student/feedback.html', details)


@transaction.atomic()
def feedback_upload(request, test_match_instance):
    """Once the user has uploaded their feedback, write it
    to a file and update the database"""
    feedback_text = request.POST["feedback"]
    feedback_sub = m.Submission(id=m.new_random_slug(m.Submission),
                                coursework=test_match_instance.coursework, creator=request.user,
                                type=m.SubmissionType.FEEDBACK, private=False)
    feedback_sub.save()
    feedback_file = m.File(submission=feedback_sub)
    feedback_file.file.save('feedback.txt', ContentFile(feedback_text))
    feedback_file.save()
    test_match_instance.feedback = feedback_sub
    test_match_instance.save()


@login_required()
def show_file(request, sub_id, filename):
    """For a given @file_id, access the filesystem and
    print out the contents of this file as a text document"""
    file = h.get_file(sub_id, filename)
    if not p.can_view_file(request.user, file):
        return HttpResponseForbidden("You are not allowed to see this file")
    return FileResponse(file.file)


@login_required()
def render_file(request, sub_id, filename):
    """For a given @file_id, access the filesystem and
    read the contents. Then pretty print the contents
    of the file as an HTML page using pygments"""
    file = h.get_file(sub_id, filename)
    # todo validate input is a text file / python script / etc. before processing. dont want to
    # todo    start trying to pretty render pdf files or executables
    if not p.can_view_file(request.user, file):
        return HttpResponseForbidden()
    content = h.read_file_by_line(file.file)
    detail = {
        "content": pyghi(content, pyglex.PythonLexer(), pygform.HtmlFormatter(linenos='table'))
    }
    return render(request, 'student/pretty_file.html', detail)
