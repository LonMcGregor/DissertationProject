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
import student.helper as h


@login_required()
def index(request):
    return render(request, 'student/index.html')


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
    state = p.state_of_user_in_coursework(request.user, cw_instance)
    msg, allow_upload, file_type, error = upload_solution_render(state)
    if error:
        return error
    if request.method == 'POST':
        result = upload_solution_post(request, cw_instance)
        if result:
            return result
        msg = "Upload of %s was completed" % request.FILES['chosen_file'],
        allow_upload = False
        file_type = None
    detail = {
        "ff": f.FileUploadForm(file_type=file_type),
        "allow_upload": allow_upload,
        "msg": msg
    }
    return render(request, 'student/upload_solution.html', detail)


def upload_solution_post(request, cw_instance):
    """Handles the POST request of the upload, and
    saves the file to the system / database. Also
    starts the job of making / running test data
    instances. Returns either an Http error code
    or False, if no error has occurred."""
    user = request.user
    upload = f.FileUploadForm(request.POST, request.FILES)
    if not upload.is_valid():
        return HttpResponseForbidden()
    if not p.user_can_upload_of_type(user, cw_instance, upload.cleaned_data['file_type']):
        return HttpResponseForbidden()
    file_type = upload.cleaned_data['file_type']
    submission = m.File(coursework=cw_instance, creator=user,
                        filepath=upload.cleaned_data['chosen_file'],
                        type=file_type)
    submission.save()
    r.new_item_uploaded(user, cw_instance, submission, file_type)
    return False


def upload_solution_render(state):
    """For a given @state,  determine
    what message to show on the upload page, and if
    an upload should be allowed at this stage.
    Return the message, allowed, and any errors"""
    if state == p.UserCourseworkState.SOLUTION:
        msg = "Please upload a solution for this coursework"
        allow_upload = True
        file_type = m.FileType.SOLUTION
    elif state == p.UserCourseworkState.TESTCASE:
        msg = "Pleaseupload a test case for this coursework"
        allow_upload = True
        file_type = m.FileType.TEST_CASE
    elif state == p.UserCourseworkState.TESTWAIT:
        msg = "Please wait for your test case to be run and results collected"
        allow_upload = False
        file_type = None
    elif state == p.UserCourseworkState.FEEDBACK:
        msg = "You may now use the feedback view to submit feedback. Please visit the coursework " \
              "detail page for more information."
        allow_upload = False
        file_type = None
    elif state == p.UserCourseworkState.COMPLETE:
        msg = "You have completed this coursework. Well done!"
        allow_upload = False
        file_type = None
    else:
        return None, None, None, HttpResponseForbidden("Invalid coursework state")
    return msg, allow_upload, file_type, False


@login_required()
def detail_coursework(request, cw=None):
    """If a coursework @cw is specified,return the page detailing it
    otherwise return a listing of all currently available tasks. """
    if cw is None or cw == "":
        available = h.retrieve_coursework(request)
        return render(request, 'student/choose_coursework.html', {'courseworks': available})
    return single_coursework(request, cw)


def single_coursework(request, coursework):
    cw = m.Coursework.objects.get(id=coursework)
    if not p.can_view_coursework(request.user, cw):
        return HttpResponseForbidden("You are not allowed to access this coursework")
    sol = h.user_submitted_file(request.user, cw, m.FileType.SOLUTION)
    test = h.user_submitted_file(request.user, cw, m.FileType.TEST_CASE)
    test_data = h.get_test_data_for_tester(request.user, coursework)
    results = test_data.results
    tester_feedback = test_data.feedback
    dev_test_data = h.get_test_data_for_developer(request.user, coursework)
    details = {
        "cw": cw,
        "solution_url": h.string_id(sol),
        "test_url": h.string_id(test),
        "test_results_url": h.string_id(results),
        "feedback_results_url": h.string_id(tester_feedback),
        "test_data": h.string_id(test_data),
        "own_feedback_data": h.string_id(dev_test_data)
    }
    return render(request, 'student/detail_coursework.html', details)


@login_required()
def feedback(request, test_data):
    """Render the page that allows a user to give feedback to a certain
    test data instance. Also handle the case of POST data upload."""
    test_data_instance = m.TestData.objects.get(id=test_data)
    perm = p.user_feedback_mode(request.user, test_data_instance)
    if perm == p.UserFeedbackModes.DENY:
        return HttpResponseForbidden("You are not allowed to see this test data")
    if perm == p.UserFeedbackModes.WAIT:
        return HttpResponse("Please wait until the test has finished running")
    if request.POST:
        if perm != p.UserFeedbackModes.WRITE:
            return HttpResponseForbidden("You are not allowed to submit feedback")
        feedback_upload(request, test_data_instance)
        return HttpResponse("Your feedback has been recorded")
    details = {
        "test_data": test_data_instance,
        "can_submit": perm == p.UserFeedbackModes.WRITE
    }
    return render(request, 'student/feedback.html', details)


@transaction.atomic()
def feedback_upload(request, test_data_instance):
    """Once the user has uploaded their feedback, write it
    to a file and update the database"""
    feedback_text = request.POST["feedback"]
    feedback_file = m.File(coursework=test_data_instance.coursework, creator=request.user,
                           type=m.FileType.FEEDBACK)
    feedback_file.filepath.save('feedback.txt', ContentFile(feedback_text))
    feedback_file.save()
    test_data_instance.feedback = feedback_file
    test_data_instance.save()


@login_required()
def show_file(request, file_id):
    """For a given @file_id, access the filesystem and
    print out the contents of this file as a text document"""
    file = m.File.objects.get(id=file_id)
    if not p.can_view_file(request.user, file):
        return HttpResponseForbidden()
    content = h.read_file_by_line(file.filepath)
    return HttpResponse(content_type="text/plain", charset="utf-8", content=content)


@login_required()
def render_file(request, file_id):
    """For a given @file_id, access the filesystem and
    read the contents. Then pretty print the contents
    of the file as an HTML page using pygments"""
    file = m.File.objects.get(id=file_id)
    if not p.can_view_file(request.user, file):
        return HttpResponseForbidden()
    content = h.read_file_by_line(file.filepath)
    detail = {
        "content": pyghi(content, pyglex.PythonLexer(), pygform.HtmlFormatter())
    }
    return render(request, 'student/pretty_file.html', detail)
