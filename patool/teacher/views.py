from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
import teacher.permission as p
import student.models as m
import teacher.forms as f


@login_required()
@p.is_teacher
def index(request, kwargs):
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
def create_course(request, kwargs):
    pass


@login_required()
@p.is_teacher
def edit_course(request, kwargs):
    # todo check exists
    # todo ADD VALIDATION - dont want overwriting IDs etc.
    if request.method=="POST":
        #todo save updates
        pass
    course = m.Course.objects.get(id=kwargs['c']) #TODO fix this
    enrollments = m.EnrolledUser.objects.filter(course=course)
    students = ""
    for eu in enrollments:
        students += str(eu.login) + ", "
    courseworks = m.Coursework.objects.filter(course=course)
    initial = {"id": course.id, "name": course.name, "student": students}
    update_form = f.CourseForm(initial)
    detail = {
        "course_name": course,
        "courseworks": courseworks,
        "uf": update_form
    }
    return render(request, 'teacher/edit_course.html', detail)


@login_required()
@p.is_teacher
def create_coursework(request):
    pass


@login_required()
@p.is_teacher
def edit_coursework(request, c=None):
    #has solutions
    #has test cases
    if request.method=="POST":
        pass
    coursework = m.Coursework.objects.get(id=c['c'])
    solutions = m.Solution.objects.filter(coursework=coursework)
    tests = []
    for solution in solutions:
        if solution.test is not None:
            tests.append(solution.test)
    initial = {"name": coursework.name,
               "descriptor": coursework.descriptor,
               "state": coursework.state}
    cw_form = f.CourseworkForm(initial)
    detail = {
        "coursework": coursework,
        "cw_form": cw_form,
        "solutions": solutions,
        "tests": tests
    }
    return render(request, 'teacher/edit_cw.html', detail)
