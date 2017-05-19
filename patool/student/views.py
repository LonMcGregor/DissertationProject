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
import django_comments.models as cm


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
        s_name = "My Test Case #%s" % str(current + 1)
        p_name = "Test Case #%s" % str(current + 1)
        t_name = str(request.user) + " Test #%s" % str(current + 1)
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

    descriptors = h.get_descriptor_tuples(cw)
    sols = h.get_solution_tuples(cw, request.user)
    tests = h.get_test_triples(cw, request.user)

    if cw.state == m.CourseworkState.UPLOAD:
        testing_data = detail_self_test_matches(request.user, cw)
    else:
        testing_data = detail_peer_feedback_group(request.user, cw)

    details = {
        "cw": cw,
        "descriptors": descriptors,
        "solution": sols,
        "tests": tests,
        "testing_data": testing_data,
        "subs_open": cw.state == m.CourseworkState.UPLOAD,
        "feedback_open": cw.state == m.CourseworkState.FEEDBACK,
        "crumbs": [("Homepage", reverse("student_index"))],

    }
    return render(request, 'student/detail_coursework.html', details)


def detail_self_test_matches(user, coursework):
    """For self testing for a @use rin a @coursework,
    prepare the match form and list results"""
    tms = [(tm, tm.solution.student_name, tm.test.student_name) for tm in
           m.TestMatch.objects.filter(type=m.TestType.SELF, coursework=coursework) if
           tm.solution.creator == user or tm.test.creator == user]
    match_form = generate_self_match_form(coursework, user)
    return [(match_form, tms, "Self-Testing", """
<ul>
    <li>You can run your tests here to make sure that your solution is working correctly</li>
    <li>You can also run your tests against the oracle to see what a correct solution does</li>
</ul>
    """)]


def detail_peer_feedback_group(user, coursework):
    """For each feedback @group that @user is a member of,
    in a given @coursework, collect the relevant files, 
    generate the form and list the test match results"""
    tm_groups = h.get_feedback_groups_for_user_in_coursework(user, coursework)
    testing_data = []
    section_title = "Peer-Testing Group %s"
    section_description = """
<ul>
<li>You can test the solutions of your peers and use their tests on your own solution</li>
<li>You can then give and receive feedback for individual test results</li>
<li>Including you, there are %s peers in this feedback group</li>
</ul>
    """
    for group in tm_groups:
        tms = h.get_all_test_matches_in_feedback_group(user, group)
        match_form = generate_peer_match_form(coursework, user, group)
        members = h.count_members_of_group(group)
        testing_data.append((match_form, tms, section_title % group.id,
                             section_description % members))
    return testing_data


def generate_self_match_form(cw, user, post=None):
    """Given a @cw instance, an @user, generate the easy
    test match form for self testing purposes.
    If the form is to be used in validating a @post request,
    this may also be passed in"""
    usable_tests = [(test.id, test.student_name) for test in m.Submission.objects.filter(
        coursework=cw, creator=user, type=m.SubmissionType.TEST_CASE)]
    usable_tests.append(('S', 'Signature Test'))
    testable_sols = [(sol.id, sol.student_name) for sol in m.Submission.objects.filter(
        coursework=cw, creator=user, type=m.SubmissionType.SOLUTION)]
    testable_sols.append(('O', 'Oracle Solution'))
    if post is None:
        return f.EasyMatchForm(usable_tests, testable_sols)
    return f.EasyMatchForm(usable_tests, testable_sols, post)


def generate_peer_match_form(cw, user, group, post=None):
    """Given a @cw instance, an @user, generate the easy
    test match form for peer testing purposes.
    If the form is to be used in validating a @post request,
    this may also be passed in"""
    all_users = h.get_all_users_in_feedback_group(group)
    user_objects = [item[0] for item in all_users]
    all_tests = m.Submission.objects.filter(coursework=cw,
                                            creator__in=user_objects,
                                            type=m.SubmissionType.TEST_CASE)
    all_sols = m.Submission.objects.filter(coursework=cw,
                                           creator__in=user_objects,
                                           type=m.SubmissionType.SOLUTION)
    tests = []
    sols = []
    for member in all_users:
        tests.extend([(t.id, t.student_name if t.creator == user else
                     member[1] + t.peer_name) for t in
                     all_tests.filter(creator=member[0], type=m.SubmissionType.TEST_CASE)])
        sols.extend([(t.id, t.student_name if t.creator == user else
                     member[1] + t.peer_name) for t in
                     all_sols.filter(creator=member[0], type=m.SubmissionType.SOLUTION)])
    tests.append(('S', 'Signature Test'))
    sols.append(('O', 'Oracle Solution'))
    if post is None:
        return f.EasyMatchForm(tests, sols, initial={"feedback_group": group.id})
    return f.EasyMatchForm(tests, sols, post)


@login_required()
def create_new_test_match(request, cw):
    """Given a coursework id, @cw, this is an entry point into creating
    a new test match, which will then be run"""
    user = request.user
    if not request.POST:
        return HttpResponseForbidden("You're supposed to POST a form here")
    coursework = m.Coursework.objects.get(id=cw)
    if not p.can_view_coursework(user, coursework):
        return HttpResponseForbidden("You're not enrolled in this course")
    if coursework.state == m.CourseworkState.UPLOAD:
        tm_form = generate_self_match_form(coursework, user, post=request.POST)
    else:
        tm_form = generate_peer_match_form(coursework, user,
                                           request.POST['feedback_group'], post=request.POST)
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
        args.append(user)
    else:
        method = matcher.create_peer_test
        args.append(tm_form.cleaned_data['feedback_group'])
    try:
        new_tm = method(*args)
        r.run_test_on_thread(new_tm, r.execute_python3_unit)
        return redirect(request, "Test Created", reverse("feedback", args=[new_tm.id]))
    except Exception as e:
        return HttpResponseForbidden(str(e))


@login_required()
def feedback(request, test_match, teacher_view=None):
    """Render the page that allows a user to give feedback to a certain
    @test_match instance. accept a @teacher_view of what crumbs to give
    teacher to allow reuse of method across both student and teacher"""
    test_match_instance = m.TestMatch.objects.get(id=test_match)
    perm = p.user_feedback_mode(request.user, test_match_instance)
    if perm == p.UserFeedbackModes.DENY:
        return HttpResponseForbidden("You are not allowed to see this test data")
    if perm == p.UserFeedbackModes.WAIT:
        return redirect(request, "Please wait until the test has finished running",
                        reverse("cw", args=[test_match_instance.coursework.id]))
    crumbs = [("Homepage", reverse("student_index")),
              ("Coursework", reverse("cw", args=[test_match_instance.coursework.id]))]
    is_teacher = teacher_view is not None
    group = h.feedback_group_for_test_match(test_match_instance)
    comment_list = [(c.submit_date, c.comment,
                     h.nick_for_user_in_group(c.user, group, request.user))
                    for c in cm.Comment.objects.filter(object_pk=test_match)]
    names = h.get_name_for_test_match(request.user, test_match_instance)
    details = {
        "test_match": test_match_instance,
        "solution_name": names[0],
        "test_name": names[1],
        "can_submit": perm == p.UserFeedbackModes.WRITE,
        "test_files": h.get_files(test_match_instance.test),
        "result_files": h.get_files(test_match_instance.result),
        "solution_files": h.get_files(test_match_instance.solution),
        "user_owns_test": test_match_instance.test.creator == request.user,
        "user_owns_sol": test_match_instance.solution.creator == request.user,
        "crumbs": crumbs if not is_teacher else teacher_view,
        "comment_list": comment_list
    }
    return render(request, 'student/feedback.html', details)


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
