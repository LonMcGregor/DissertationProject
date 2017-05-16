from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse

from runner import matcher
import runner.runner as r
import student.forms as f
import student.helper as h
import student.models as m
import student.permission as p
import runner.pipelines as pipe


@login_required()
def index(request):
    return detail_coursework(request)


@login_required()
def upload_submission(request, cw=None):
    """Given a @request, handle a POST upload form
    for the specified coursework @cw."""
    if request.method != "POST":
        return HttpResponseForbidden("You can only POST a form here")
    no_cws = m.Coursework.objects.filter(id=cw).count() != 1
    if cw is None or cw == "" or no_cws:
        return Http404("No coursework has been specified")
    cw_instance = m.Coursework.objects.get(id=cw)
    if not p.can_view_coursework(request.user, cw_instance):
        return HttpResponseForbidden("You are not allowed to see this coursework")
    file_type = request.POST['file_type']
    if not p.user_can_upload_of_type(request.user, cw_instance, file_type):
        return HttpResponseForbidden("You can't upload submissions of this type")
    # todo if submitting a new solution, clear the old one first
    if file_type == m.SubmissionType.SOLUTION:
        h.delete_old_solution(request.user, cw_instance)
        s_name = "My Solution"
        p_name = "Solution"
        t_name = str(request.user) + " Sol"
        sub = save_submission(cw_instance, request, file_type, s_name, p_name, t_name)
        pipe.python_solution(sub)
        msg = "Your solution has been tested using the signature test. You should check the " \
              "results of this test to make sure that our solution is written correctly "
    else:
        current = m.Submission.objects.filter(coursework=cw_instance, creator=request.user).count()
        s_name = "My Test Case #%s" % str(current+1)
        p_name = "Test Case #%s" % str(current+1)
        t_name = str(request.user) + " Test #%s" % str(current+1)
        save_submission(cw_instance, request, file_type, s_name, p_name, t_name)
        msg = "You can run your newly uploaded test against the oracle to make sure that you are " \
              "testing for the correct output "
        # todo note this counting will end up being incorrect if user deletes something
        # todo it may end up being better to dynamically generate names
    return redirect(request, "Upload completed." + msg, reverse("cw", args=[cw]))


@transaction.atomic
def save_submission(cw_instance, request, file_type, s_name, p_name, t_name):
    """Do the atomic database actions required to save the new files"""
    submission = m.Submission(id=m.new_random_slug(m.Submission), coursework=cw_instance,
                              creator=request.user, type=file_type,
                              student_name=s_name,
                              peer_name=p_name,
                              teacher_name=t_name)
    submission.save()
    for each in request.FILES.getlist('chosen_files'):
        m.File(file=each, submission=submission).save()
    return submission


@login_required()
def upload_test(request, cw=None):
    """Given a @request to upload a test to @cw
    render the submission form for test cases"""
    no_cws = m.Coursework.objects.filter(id=cw).count() != 1
    if cw is None or cw == "" or no_cws:
        return Http404("No coursework has been specified")
    cw_instance = m.Coursework.objects.get(id=cw)
    if not p.can_view_coursework(request.user, cw_instance):
        return HttpResponseForbidden("You are not allowed to see this coursework")
    state = p.state_of_user_in_coursework(request.user, cw_instance)
    detail = {
        "msg": "Upload Test Case for coursework",
        "allow_upload": state in [p.UserCourseworkState.UPLOADS, p.UserCourseworkState.FEEDBACK],
        "file_type": "c",
        "cw": cw,
        "crumbs": [("Homepage", reverse("student_index")),
                   ("Coursework", reverse("cw", args=[cw]))]
    }
    return render(request, 'student/upload_solution.html', detail)


@login_required()
def upload_solution(request, cw=None):
    """Given a @request to upload a solution to @cw
    render the submission form for solutions"""
    no_cws = m.Coursework.objects.filter(id=cw).count() != 1
    if cw is None or cw == "" or no_cws:
        return Http404("No coursework has been specified")
    cw_instance = m.Coursework.objects.get(id=cw)
    if not p.can_view_coursework(request.user, cw_instance):
        return HttpResponseForbidden("You are not allowed to see this coursework")
    state = p.state_of_user_in_coursework(request.user, cw_instance)
    detail = {
        "msg": "(Re-)Upload Solution for coursework",
        "allow_upload": state == p.UserCourseworkState.UPLOADS,
        "file_type": "s",
        "cw": cw,
        "crumbs": [("Homepage", reverse("student_index")),
                   ("Coursework", reverse("cw", args=[cw]))]
    }
    return render(request, 'student/upload_solution.html', detail)


@login_required()
def detail_coursework(request, cw=None):
    """If a coursework @cw is specified,return the page detailing it
    otherwise return a listing of all currently available tasks. """
    if cw is None or cw == "":
        return render(request, 'student/choose_coursework.html',
                      {'courseworks': p.coursework_available_for_user(request.user)})
    return single_coursework(request, cw)


def single_coursework(request, cwid):
    """Given a @request for the details for
    coursework @cwid, generate the page"""
    cw = m.Coursework.objects.get(id=cwid)
    if not p.can_view_coursework(request.user, cw):
        return HttpResponseForbidden("You are not allowed to access this coursework")

    descriptors = [(s, h.get_files(s)) for s in m.Submission.objects.filter(
        type=m.SubmissionType.CW_DESCRIPTOR, coursework=cw)]
    solution = [(s, h.get_files(s)) for s in m.Submission.objects.filter(
        coursework=cw, creator=request.user, type=m.SubmissionType.SOLUTION)]
    tests = [(t, h.get_files(t), h.can_delete(t)) for t in m.Submission.objects.filter(
        coursework=cw, creator=request.user, type=m.SubmissionType.TEST_CASE)]

    if cw.state == m.CourseworkState.UPLOAD:
        tms = [tm for tm in m.TestMatch.objects.filter(
            type=m.TestType.SELF, coursework=cw
        ) if tm.solution.creator == request.user or tm.test.creator == request.user]
    else:
        # todo get testing group
        tm_group = [1, 2, 3]
        tms = [tm for tm in m.TestMatch.objects.filter(
            type=m.TestType.PEER, coursework=cw
        ) if tm in tm_group]

    easy_match_form = generate_easy_match_form(cw, request.user)

    details = {
        "cw": cw,
        "descriptors": descriptors,
        "solution": solution,
        "tests": tests,
        "tms": tms,
        "subs_open": cw.state == m.CourseworkState.UPLOAD,
        "feedback_open": cw.state == m.CourseworkState.FEEDBACK,
        "crumbs": [("Homepage", reverse("student_index"))],
        "easy_match_form": easy_match_form
    }
    return render(request, 'student/detail_coursework.html', details)


def generate_easy_match_form(cw, user, post=None):
    """Given a @cw instance, an @user, generate the easy
    test match form.
    If the form is to be used in validating a @post request,
    this may also be passed in"""
    tests = [t for t in m.Submission.objects.filter(
        coursework=cw, creator=user, type=m.SubmissionType.TEST_CASE)]
    solution = [s for s in m.Submission.objects.filter(
        coursework=cw, creator=user, type=m.SubmissionType.SOLUTION)]
    usable_tests = [(test.id, test.student_name) for test in tests]
    usable_tests.append(('S', 'Signature Test'))
    if cw.state == m.CourseworkState.UPLOAD:
        testable_sols = [(sol.id, sol.student_name) for sol in solution]
    else:
        testable_sols = []
        # todo the solutions for everyone in the testing group except mine
    testable_sols.append(('O', 'Oracle Solution'))
    if post is None:
        return f.EasyMatchForm(usable_tests, testable_sols)
    return f.EasyMatchForm(usable_tests, testable_sols, post)


@login_required()
def create_new_test_match(request, cw):
    """Given a coursework id, @cw, this is an entry point into creating
    a new test match, which will then be run"""
    if not request.POST:
        return HttpResponseForbidden("You're supposed to POST a form here")
    coursework = m.Coursework.objects.get(id=cw)
    if not p.can_view_coursework(request.user, coursework):
        return HttpResponseForbidden("You're not enrolled in this course")
    tm_form = generate_easy_match_form(coursework, request.user, post=request.POST)
    if not tm_form.is_valid():
        return HttpResponseForbidden("Invalid form data")
    if coursework.state not in [m.CourseworkState.UPLOAD, m.CourseworkState.FEEDBACK]:
        return HttpResponseForbidden("This coursework isn't accepting new test matches")
    args = [
        tm_form.cleaned_data['solution'],
        tm_form.cleaned_data['test'],
        coursework
    ]
    if coursework.state == m.CourseworkState.UPLOAD:
        method = matcher.create_self_test
        args.append(request.user)
    else:
        method = matcher.create_peer_test
    try:
        new_tm = method(*args)
        r.run_test_on_thread(new_tm, r.execute_python3_unit)
    except Exception as e:
        return HttpResponseForbidden(str(e))
    return redirect(request, "Test Created", reverse("cw", args=[cw]))


@login_required()
def feedback(request, test_match, teacher_view=None):
    """Render the page that allows a user to give feedback to a certain
    test data instance. Also handle the case of POST data upload."""
    test_match_instance = m.TestMatch.objects.get(id=test_match)
    perm = p.user_feedback_mode(request.user, test_match_instance)
    if perm == p.UserFeedbackModes.DENY:
        return HttpResponseForbidden("You are not allowed to see this test data")
    if perm == p.UserFeedbackModes.WAIT:
        return redirect(request, "Please wait until the test has finished running",
                        reverse("cw", args=[test_match_instance.coursework.id]))
    if request.POST:
        if perm != p.UserFeedbackModes.WRITE:
            return HttpResponseForbidden("You are not allowed to submit feedback")
        feedback_upload(request, test_match_instance)
        return redirect(request, "Your feedback has been recorded",
                        reverse("feedback", args=[test_match_instance.id]))
    crumbs = [("Homepage", reverse("student_index")),
              ("Coursework", reverse("cw", args=[test_match_instance.coursework.id]))]
    if teacher_view is not None:
        crumbs = teacher_view
    # feedback_files = h.get_files(test_match_instance.feedback)
    details = {
        "test_match": test_match_instance,
        "can_submit": perm == p.UserFeedbackModes.WRITE,
        "test_files": h.get_files(test_match_instance.test),
        "result_files": h.get_files(test_match_instance.result),
        "solution_files": h.get_files(test_match_instance.solution),
        "user_owns_test": test_match_instance.test.creator == request.user,
        "user_owns_sol": test_match_instance.solution.creator == request.user,
        # "feedback_files": feedback_files if len(feedback_files) > 0 else None,
        # todo for now, assume only 1 files
        "crumbs": crumbs
    }
    return render(request, 'student/feedback.html', details)


@transaction.atomic()
def feedback_upload(request, test_match_instance):
    """Once the user has uploaded their feedback, write it
    to a file and update the database
    feedback_text = request.POST["feedback"]
    feedback_sub = m.Submission(id=m.new_random_slug(m.Submission),
                                coursework=test_match_instance.coursework, creator=request.user,
                                type=m.SubmissionType.FEEDBACK, private=False)
    feedback_sub.save()
    feedback_file = m.File(submission=feedback_sub)
    feedback_file.file.save('feedback.txt', ContentFile(feedback_text))
    feedback_file.save()
    test_match_instance.feedback = feedback_sub
    test_match_instance.save()"""
    return


@login_required()
@transaction.atomic()
def delete_submission(request):
    """A user has requested deletion of a file, with id in post"""
    sub_id = request.POST['sub_id']
    cw = m.Submission.objects.get(id=sub_id).coursework
    status = h.delete_submission(request.user, m.Submission.objects.get(id=sub_id))
    if status:
        return redirect(request, "Submission Deleted", reverse("cw", args=[cw.id]))
    return redirect(request, "Failed to delete file", reverse("cw", args=[cw.id]))


def redirect(request, message, location):
    """Render a view that does pretty auto-redirection
    for  a given @request, showing @message and leading
    to the specified @location"""
    return render(request,
                  'common/redirect.html',
                  {"message": message,
                   "redirect": location})
