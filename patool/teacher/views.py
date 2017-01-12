from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import teacher.permission as p
import student.models as m
import teacher.forms as f
from django.db import transaction


@login_required()
@p.is_teacher
def index(request):
    me = request.user
    enrolled_in = m.EnrolledUser.objects.filter(login=me)
    my_courses = []
    for enrollment in enrolled_in:
        my_courses.append(enrollment.course)
    detail = {
        "courses": my_courses
    }
    return render(request, 'teacher/index.html', detail)


@login_required()
@p.is_teacher
def create_course(request):
    if request.method == "POST":
        return create_course_update(request, request.POST)
    return create_course_render(request)


def create_course_render(request):
    detail = {
        "course_name": "New Course",
        "courseworks": [],
        "uf": f.CourseForm({"student": str(request.user)+','})
    }
    return render(request, 'teacher/edit_course.html', detail)


@transaction.atomic
def create_course_update(request, new_details):
    owner = request.user

    # todo ADD VALIDATION - dont want overwriting IDs etc.
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
    requested_course_code = kwargs['c']
    if request.method == "POST":
        edit_course_update(request, requested_course_code, request.POST)
    return edit_course_render(request, requested_course_code)


@transaction.atomic
def edit_course_update(request, course_code, new_details):
    # todo ADD VALIDATION - dont want overwriting IDs etc.
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
    course = m.Course.objects.get(code=requested_course_code)
    enrollments = m.EnrolledUser.objects.filter(course=course)
    students = ""
    for eu in enrollments:
        students += str(eu.login) + ", "
    courseworks = m.Coursework.objects.filter(course=course)
    initial = {"id": course.id, "name": course.name, "student": students}
    update_form = f.CourseForm(initial)
    detail = {
        "course_name": course.name,
        "course_code": course.code,
        "courseworks": courseworks,
        "uf": update_form
    }
    return render(request, 'teacher/edit_course.html', detail)


@login_required()
@p.is_teacher
def create_coursework(request, kwargs):
    requested_course_code = kwargs['c']
    if request.method == "POST":
        return create_coursework_update(request.POST, requested_course_code)
    return create_coursework_render(request)


def create_coursework_render(request):
    detail = {
        "courseworks": {"name": "New Coursework"},
        "cw_form": f.CourseworkForm(),
        "solutions": [],
        "tests": []
    }
    return render(request, 'teacher/edit_cw.html', detail)


@transaction.atomic
def create_coursework_update(new_details, course_code):
    # todo ADD VALIDATION - dont want overwriting IDs etc.
    updated_form = f.CourseworkForm(new_details)
    if not updated_form.is_valid():
        raise Exception("validity problem")
    new_name = updated_form.cleaned_data['name']
    new_descriptor = updated_form.cleaned_data['descriptor']
    new_state = updated_form.cleaned_data['state']

    course = m.Course.objects.get(code=course_code)
    coursework = m.Coursework(name=new_name, descriptor=new_descriptor, course=course,
                              state=new_state)
    coursework.save()
    return redirect('edit_cw', c=coursework.id)


@login_required()
@p.is_teacher
def edit_coursework(request, kwargs=None):
    coursework = m.Coursework.objects.get(id=kwargs['c'])
    if request.method == "POST":
        edit_coursework_update(request.POST, coursework)
    return edit_coursework_render(request, coursework)


def edit_coursework_update(new_details, old_coursework):
    updated_form = f.CourseworkForm(new_details)
    if not updated_form.is_valid():
        raise Exception("validity problem")
    old_coursework.name = updated_form.cleaned_data['name']
    old_coursework.descriptor = updated_form.cleaned_data['descriptor']
    old_coursework.state = updated_form.cleaned_data['state']
    old_coursework.save()


def edit_coursework_render(request, coursework):
    files = m.File.objects.filter(coursework=coursework)
    results = m.TestData.objects.filter(coursework=coursework)
    initial = {"name": coursework.name,
               "descriptor": coursework.descriptor,
               "state": coursework.state}
    cw_form = f.CourseworkForm(initial)
    detail = {
        "coursework": coursework,
        "cw_form": cw_form,
        "files": files,
        "results": results
    }
    return render(request, 'teacher/edit_cw.html', detail)
