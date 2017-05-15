from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse

import runner.runner as r
import student.helper as h
import student.models as m
import teacher.forms as f
import student.forms as sf
import teacher.permission as p
import student.views as student_views
from runner import matcher
from runner import runner


@login_required()
@p.is_teacher
def index(request):
    """Show all of the courses available for the
    logged in teacher as a list"""
    enrolled_in = m.EnrolledUser.objects.filter(login=request.user)
    my_courses = [x.course for x in enrolled_in]
    detail = {
        "courses": my_courses
    }
    return render(request, 'teacher/index.html', detail)


@login_required()
@p.is_teacher
def create_course(request):
    """Handle the creation of a course, or create the form to do so"""
    if request.method == "POST":
        return create_course_update(request, request.POST)
    return create_course_render(request)


def create_course_render(request):
    """Generate the form used to create a course"""
    detail = {
        "course_name": "New Course",
        "courseworks": None,
        "uf": f.CourseForm({"student": str(request.user) + ','}),
        "crumbs": [("Homepage", reverse("teacher_index"))]
    }
    return render(request, 'teacher/edit_course.html', detail)


@transaction.atomic
def create_course_update(request, new_details):
    """Given the @new_details from a course, create a new course.
    Also handle enrolling all of the specified users. The
    owner of the course is not allowed to remove themselves"""
    owner = request.user
    updated_form = f.CourseForm(new_details)
    if not updated_form.is_valid():
        raise Exception("validity problem")
    new_code = updated_form.cleaned_data['code']
    new_name = updated_form.cleaned_data['name']
    new_students = updated_form.cleaned_data['student'].strip().strip(',').split(',')
    new_students_list = list(map(lambda w: w.strip(), new_students))

    course = m.Course(code=new_code, name=new_name)
    course.save()

    for item in new_students_list:
        current_user = m.User.objects.get(username=item)
        new_item = m.EnrolledUser(login=current_user, course=course)
        new_item.save()

    if str(owner) not in new_students_list:
        new_item = m.EnrolledUser(login=owner, course=course)
        new_item.save()

    return redirect(request, "Course created", reverse('edit_course', args=[new_code]))


@login_required()
@p.is_teacher
def edit_course(request, c):
    """Handle creation of form, or post request for editing a course"""
    cw = m.Course.objects.get(code=c)
    if not p.is_enrolled_on_course(request.user, cw):
        return HttpResponseForbidden("You are not enrolled on this course")
    if request.method == "POST":
        edit_course_update(request, requested_course_code, request.POST)
    return edit_course_render(request, requested_course_code)


@transaction.atomic
def edit_course_update(request, course_code, new_details):
    """Given the @new_details for @course_code, update
    these details in the database, and handle any updates
    needed with regards to enrolled users"""
    owner = request.user
    old_course = m.Course.objects.get(code=course_code)
    updated_form = f.CourseForm(new_details)
    if not updated_form.is_valid():
        raise Exception("validity problem")
    old_course.code = updated_form.cleaned_data['code']
    old_course.name = updated_form.cleaned_data['name']
    old_course.save()

    new_students = updated_form.cleaned_data['student'].strip().strip(',').split(',')
    new_students_list = list(map(lambda w: w.strip(), new_students))

    enrollments = m.EnrolledUser.objects.filter(course=old_course)
    for item in enrollments:
        if item.login == owner:
            continue
        if str(item.login) not in new_students_list:
            item.delete()
    for item in new_students_list:
        current_user = m.User.objects.get(username=item)
        exists = m.EnrolledUser.objects.filter(login=current_user).filter(course=old_course)
        if exists.count() != 1:
            new_item = m.EnrolledUser(login=current_user, course=old_course)
            new_item.save()


def edit_course_render(request, requested_course_code):
    """Get the details of @requested_course_code, coursework
    items and all the enrolled users and then
    populate the form before displaying it to user"""
    course = m.Course.objects.get(code=requested_course_code)
    enrollments = m.EnrolledUser.objects.filter(course=course)
    students = ""
    for eu in enrollments:
        students += str(eu.login) + ", "
    courseworks = m.Coursework.objects.filter(course=course)
    initial = {"code": course.code, "name": course.name, "student": students}
    update_form = f.CourseForm(initial)
    detail = {
        "course_name": course.name,
        "course_code": course.code,
        "courseworks": courseworks,
        "uf": update_form,
        "crumbs": [("Homepage", reverse("teacher_index"))]
    }
    return render(request, 'teacher/edit_course.html', detail)


@login_required()
@p.is_teacher
def create_coursework(request, c):
    """Handle form for creating a coursework in course @[c]"""
    cw = m.Course.objects.get(code=c)
    if not p.is_enrolled_on_course(request.user, cw):
        return HttpResponseForbidden("You are not enrolled on this course")
    if request.method == "POST":
        return create_coursework_update(request.user, request, requested_course_code)
    return create_coursework_render(request, requested_course_code)


def create_coursework_render(request, code):
    """Generate an empty form for creating a coursework for course @code"""
    detail = {
        "courseworks": {"name": "New Coursework"},
        "cw_form": False,
        "descriptor": [],
        "oracle_exec": [],
        "identity": [],
        "solutions": [],
        "tests": [],
        "crumbs": [("Homepage", reverse("teacher_index")),
                   ("Course", reverse("edit_course", args=[code]))]
    }
    return render(request, 'teacher/edit_cw.html', detail)


@transaction.atomic
def create_coursework_update(user, request, course_code):
    """@user - Given the @request for a coursework, and
    the @course_code we want to add it to, update the db"""
    new_name = request.POST['name']
    new_state = request.POST['state']
    course = m.Course.objects.get(code=course_code)
    coursework = m.Coursework(id=m.new_random_slug(m.Coursework), name=new_name,
                              course=course, state=new_state, file_pipe="runner.py",
                              test_pipe="runner.py")
    coursework.save()

    descriptor = m.Submission(id=m.new_random_slug(m.Submission), coursework=coursework,
                              creator=user, type=m.SubmissionType.CW_DESCRIPTOR,
                              student_name="Coursework Descriptor",
                              teacher_name="Descriptor")
    descriptor.save()
    for each in request.FILES.getlist('descriptor'):
        m.File(file=each, submission=descriptor).save()

    oracle_exec = m.Submission(id=m.new_random_slug(m.Submission), coursework=coursework,
                               creator=user, type=m.SubmissionType.ORACLE_EXECUTABLE,
                               student_name="Oracle Solution",
                               teacher_name="Oracle")
    oracle_exec.save()
    for each in request.FILES.getlist('oracle_exec'):
        m.File(file=each, submission=oracle_exec).save()

    sig = m.Submission(id=m.new_random_slug(m.Submission), coursework=coursework,
                       creator=user, type=m.SubmissionType.SIGNATURE_TEST,
                       student_name="Signature Test",
                       teacher_name="Signature")
    sig.save()
    for each in request.FILES.getlist('identity'):
        m.File(file=each, submission=sig).save()

    return redirect(request, "Coursework created", reverse('edit_cw', args=[coursework.id]))


@login_required()
@p.is_teacher
def edit_coursework(request, c):
    """Prepare a page to view and edit coursework @[c]"""
    coursework = m.Coursework.objects.get(id=c)
    if not p.is_enrolled_on_course(request.user, coursework.course):
        return HttpResponseForbidden("You are not enrolled on this course")
    if request.method == "POST":
        edit_coursework_update(request.POST, coursework)
    return edit_coursework_render(request, coursework)


@transaction.atomic()
def edit_coursework_update(new_details, old_coursework):
    """Given the @new_details, update the database for
    the details o @old_coursework"""
    updated_form = f.CourseworkForm(new_details)
    if not updated_form.is_valid():
        raise Exception("validity problem")
    old_coursework.name = updated_form.cleaned_data['name']
    old_coursework.state = updated_form.cleaned_data['state']
    old_coursework.save()


def edit_coursework_render(request, coursework):
    """Get all of the necessary details to display a
    page for a given @coursework, including the
    file suploaded for it, test data instances and
    of course the metadata about the coursework itself"""
    desc_types = [m.SubmissionType.CW_DESCRIPTOR, m.SubmissionType.ORACLE_EXECUTABLE,
                  m.SubmissionType.SIGNATURE_TEST]
    submissions = [(s, h.get_files(s)) for s in m.Submission.objects.filter(
        coursework=coursework, type__in=desc_types)]
    initial = {"name": coursework.name,
               "state": coursework.state}
    cw_form = f.CourseworkForm(initial)
    detail = {
        "coursework": coursework,
        "cw_form": cw_form,
        "submissions": submissions,
        "crumbs": [("Homepage", reverse("teacher_index")),
                   ("Course", reverse("edit_course", args=[coursework.course.code]))]
    }
    return render(request, 'teacher/edit_cw.html', detail)


@login_required()
@p.is_teacher
def view_coursework(request, c):
    """A teacher has made a @request to view the view
    page for coursewok with @[c]. display files, tests"""
    coursework = m.Coursework.objects.get(id=c)
    if not p.is_enrolled_on_course(request.user, coursework.course):
        return HttpResponseForbidden("You are not enrolled on this course")
    submissions = [(s, h.get_files(s)) for s in
                   m.Submission.objects.filter(coursework=coursework)
                   .exclude(type=m.SubmissionType.FEEDBACK)
                   .exclude(type=m.SubmissionType.TEST_RESULT)]
    tm_initial = {"coursework": coursework.id}
    tm_form = generate_teacher_easy_match_form(coursework)
    atm_form = f.AutoTestMatchForm(tm_initial)
    results = m.TestMatch.objects.filter(coursework=coursework)
    detail = {
        "coursework": coursework,
        "submissions": submissions,
        "tm_form": tm_form,
        "atm_form": atm_form,
        "results": results,
        "crumbs": [("Homepage", reverse("teacher_index")),
                   ("Course", reverse("edit_course", args=[coursework.course.code]))]

    }
    return render(request, 'teacher/view_cw.html', detail)


def generate_teacher_easy_match_form(coursework, post=None):
    """Given an instance of @coursework, generate a
    relevant easymatchform"""
    tests = [(t.id, t.teacher_name) for t in m.Submission.objects.filter(
        coursework=coursework, type__in=[m.SubmissionType.TEST_CASE, m.SubmissionType.SIGNATURE_TEST])]
    solutions = [(s.id, s.teacher_name) for s in m.Submission.objects.filter(
        coursework=coursework, type__in=[m.SubmissionType.SOLUTION, m.SubmissionType.ORACLE_EXECUTABLE])]
    if post is None:
        return sf.EasyMatchForm(tests, solutions)
    return sf.EasyMatchForm(tests, solutions, post)


@login_required()
@p.is_teacher
def create_test_match(request, c):
    """Create a new test match, according to what is specified in the POST request"""
    coursework = m.Coursework.objects.get(id=c)
    if not request.POST:
        return HttpResponseForbidden("You're supposed to POST a form here")
    if not p.is_enrolled_on_course(request.user, coursework.course):
        return HttpResponseForbidden("You're not enrolled on this course")
    if "algorithm" in request.POST:
        return auto_test_match_update(request, coursework)
    else:
        return manual_test_match_update(request, coursework)


def manual_test_match_update(request, coursework):
    """Create a new test match with data specified in @request for @coursework"""
    tm_form = generate_teacher_easy_match_form(coursework, request.POST)
    if not tm_form.is_valid():
        return HttpResponseBadRequest("Invalid form data")
    try:
        new_tm = matcher.create_peer_test(
            tm_form.cleaned_data['solution'],
            tm_form.cleaned_data['test'],
            coursework.id,
            True
        )
        runner.run_test_on_thread(new_tm, runner.execute_python3_unit)
    except Exception as e:
        return HttpResponseBadRequest(str(e))
    return redirect(request, "Test created",
                    reverse('view_cw', args=[coursework.id]))


def auto_test_match_update(request, coursework):
    """Given an @request, extract the form data and call an automatic
    test match creation algorithm and run in @coursework"""
    atm = f.AutoTestMatchForm(request.POST)
    if not atm.is_valid():
        return HttpResponseBadRequest("Invalid form data")
    try:
        matcher.first_available(
            coursework.id,
            request.user,
            atm.cleaned_data['assign_markers'],
            atm.cleaned_data['visible_to_developer']
        )
    except Exception as e:
        return HttpResponseBadRequest(str(e))
    return redirect(request, "Tests created",
                    reverse('view_cw', args=[atm.cleaned_data['coursework']]))


@login_required()
@p.is_teacher
def run_all_test_in_cw(request, c):
    """Run all of the queued tests for coursework with id @c"""
    cw = m.Coursework.objects.get(id=c)
    if not p.is_enrolled_on_course(request.user, cw.course):
        return HttpResponseForbidden("you're not enrolled on this course")
    r.run_all_queued_on_thread(cw)
    return redirect(request, "Starting to run queued tests", reverse('view_cw', args=[cw.id]))


@login_required()
@p.is_teacher
@transaction.atomic()
def update_content(request):
    if request.method != "POST":
        return HttpResponseForbidden("You are only allowed to POST here")
    old_sub = m.Submission.objects.get(id=request.POST['old_id'])
    if not p.is_enrolled_on_course(request.user, old_sub.coursework.course):
        return HttpResponseForbidden("you're not enrolled on this course")

    new_sub = m.Submission(id=m.new_random_slug(m.Submission), coursework=old_sub.coursework,
                           creator=request.user, type=old_sub.type,
                           student_name=old_sub.student_name,
                           peer_name=old_sub.peer_name,
                           teacher_name=old_sub.teacher_name)
    new_sub.save()
    old_sub.delete()
    for each in request.FILES.getlist('new_content'):
        m.File(file=each, submission=new_sub).save()

    return redirect(request, "Content Updated", reverse('edit_cw', args=[new_sub.coursework.id]))


def redirect(request, message, location):
    """Render a view that does pretty auto-redirection
    for  a given @request, showing @message and leading
    to the specified @location"""
    return render(request,
                  'common/redirect.html',
                  {"message": message,
                   "redirect": location})

@login_required
def view_test(request, c, t):
    """Render the virw showing tets details (feedback view)
    from the student app, but add teacher specific links
    given id for coursework @c and test @t"""
    return student_views.feedback(request, t, [
        ("Homepage", reverse("teacher_index")),
        ("Coursework", reverse("view_cw", args=[c]))
    ])