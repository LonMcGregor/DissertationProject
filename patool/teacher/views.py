from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import teacher.permission as p
import student.models as m
import student.helper as h
import teacher.forms as f
from django.db import transaction
import student.runner as r
from django.http import HttpResponseForbidden, HttpResponse
import threading
from django.contrib.auth.models import User


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
        "uf": f.CourseForm({"student": str(request.user)+','}),
        "crumbs": [("Homepage", "/teacher")]
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

    return redirect('edit_course', c=new_code)


@login_required()
@p.is_teacher
def edit_course(request, kwargs):
    """Handle creation of form, or post request for editing a course"""
    requested_course_code = kwargs['c']
    cw = m.Course.objects.get(code=requested_course_code)
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
        "crumbs": [("Homepage", "/teacher")]
    }
    return render(request, 'teacher/edit_course.html', detail)


@login_required()
@p.is_teacher
def create_coursework(request, kwargs):
    """Handle form for creating a coursework in course @[c]"""
    requested_course_code = kwargs['c']
    cw = m.Course.objects.get(code=requested_course_code)
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
        "crumbs": [("Homepage", "/teacher"), ("Course", "/teacher/course/%s" % code)]
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
                              creator=user, type=m.SubmissionType.CW_DESCRIPTOR, private=False)
    descriptor.save()
    for each in request.FILES.getlist('descriptor'):
        m.File(file=each, submission=descriptor).save()

    oracle_exec = m.Submission(id=m.new_random_slug(m.Submission), coursework=coursework,
                               creator=user, type=m.SubmissionType.ORACLE_EXECUTABLE, private=False)
    oracle_exec.save()
    for each in request.FILES.getlist('oracle_exec'):
        m.File(file=each, submission=oracle_exec).save()

    identity = m.Submission(id=m.new_random_slug(m.Submission), coursework=coursework,
                            creator=user, type=m.SubmissionType.IDENTITY_TEST, private=False)
    identity.save()
    for each in request.FILES.getlist('identity'):
        m.File(file=each, submission=identity).save()

    return redirect('edit_cw', c=coursework.id)


@login_required()
@p.is_teacher
def edit_coursework(request, kwargs=None):
    """Prepare a page to view and edit coursework @[c]"""
    coursework = m.Coursework.objects.get(id=kwargs['c'])
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
    submissions = [(s, h.get_files(s)) for s in m.Submission.objects.filter(coursework=coursework)]
    results = m.TestMatch.objects.filter(coursework=coursework)
    initial = {"name": coursework.name,
               "state": coursework.state}
    tm_initial = {"coursework": coursework.id, "visible_to_developer": True}
    cw_form = f.CourseworkForm(initial)
    tm_form = f.TestMatchForm(tm_initial)
    detail = {
        "coursework": coursework,
        "cw_form": cw_form,
        "tm_form": tm_form,
        "submissions": submissions,
        "results": results,
        "crumbs": [("Homepage", "/teacher"),
                   ("Course", "/teacher/course/%s" % coursework.course.code)]
    }
    return render(request, 'teacher/edit_cw.html', detail)


@login_required()
@p.is_teacher
def force_start_test_run(request, kwargs):
    """Given a particular test data id @[t], force it to run"""
    requested_test = kwargs['t']
    test_instance = m.TestMatch.objects.get(id=requested_test)
    if not test_instance.waiting_to_run:
        return HttpResponseForbidden("Test has already been run")
    if not p.is_enrolled_on_course(request.user, test_instance.coursework.course):
        return HttpResponseForbidden("You are not enrolled on this course")
    r.run_test_on_thread(test_instance)
    return HttpResponse("Test Run %s Force Started" % kwargs['t'])


@login_required()
@p.is_teacher
@transaction.atomic()
def create_test_match(request):
    if not request.POST:
        return HttpResponseForbidden("You're supposed to POST a form here")
    tm_form = f.TestMatchForm(request.POST)
    if not tm_form.is_valid():
        return HttpResponseForbidden("Invalid form data")
    solution = m.Submission.objects.get(id=tm_form.cleaned_data['solution_sub'])
    test_case = m.Submission.objects.get(id=tm_form.cleaned_data['test_sub'])
    if solution.type != m.SubmissionType.SOLUTION or test_case.type != m.SubmissionType.TEST_CASE:
        return HttpResponseForbidden("Need 1 solution and 1 test")
    cw = m.Coursework.objects.get(id=tm_form.cleaned_data['coursework'])
    marker = User.objects.get(username=tm_form.cleaned_data['to_be_marked_by'])
    if m.EnrolledUser.objects.filter(course=cw.course, login=marker).count() != 1:
        return HttpResponseForbidden("You're not allowed to edit this course")
    new_tm = m.TestMatch(id=m.new_random_slug(m.TestMatch), test=test_case, solution=solution,
                         coursework=cw, initiator=request.user, waiting_to_run=True,
                         visible_to_developer=tm_form.cleaned_data['visible_to_developer'],
                         marker=marker)
    new_tm.save()
    return HttpResponse("Test has been created")
