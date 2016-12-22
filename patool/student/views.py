from django.http import Http404, HttpResponseForbidden, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import student.models as m
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.db import transaction


@login_required()
def index(request):
    return render(request, 'student/index.html')


@login_required()
def upload_solution(request, singlecw=None):
    # todo verify the upload should occur
    if singlecw is None or singlecw == "":
        return Http404()
    if request.method == 'POST':
        cw = m.Coursework.objects.get(id=singlecw)
        s = m.Solution(coursework=cw, developer=request.user, filepath=request.FILES['chosenfile'])
        s.save()
        detail = {
            "is_upload": True,
            "filename": request.FILES['chosenfile'],
            "cw": singlecw
        }
    else:
        detail = {
            "is_upload": False,
            "cw": singlecw
        }
    return render(request, 'student/upload_solution.html', detail)


def push_test(request):
    return render(request, 'student/pushtest.html')


def retrieve_coursework(request):
    """For a given @request, return a list of courseworks available to the user"""
    logged_in_user = request.user
    enrolled_courses = m.EnrolledUser.objects.filter(login=logged_in_user).values('course')
    courses_for_user = m.Course.objects.filter(id__in=enrolled_courses)
    all_courseworks_for_user = m.Coursework.objects.filter(course__in=courses_for_user)
    #courseworks = filter(lambda a: a.is_visible(),)
    return all_courseworks_for_user.values_list('id', 'state', 'course', 'name').order_by('state')


@login_required()
def detail_coursework(request, singlecw=None):
    if singlecw is None or singlecw == "":
        available = retrieve_coursework(request)
        return render(request, 'student/choose_coursework.html', {'courseworks': available})
    details = {
        "name": "binary tree",
        "cwid": singlecw,
        "descript": "http://example.com/descriptor.pdf",
    }
    #get coursework from db
    cw = m.Coursework.objects.get(id=singlecw)
    #check permission to view it
    #check submission status
    sol = False
    test = False
    test_run = False
    ass = False
    details = {
        "cw": cw,
        "solution": sol,
        "test": test,
        "testrun": test_run,
        "assess": ass
    }
    return render(request, 'student/detail_coursework.html', details)


@transaction.atomic
def populate_database(request):
    if settings.DEBUG:
        t = Group()
        t.name = "teacher"
        t.save()
        s = Group()
        s.name = "student"
        s.save()

        cu = User.objects.create_user

        w = cu("winston", password="primalrage")
        w.groups.add(t)
        w.save()

        z = cu("zenyatta", password="transcendence")
        z.groups.add(t)
        z.save()

        sy = cu("symmetra", password="teleporter")
        sy.groups.add(t)
        sy.save()

        a = cu("ana", password="nanoboost")
        a.groups.add(s)
        a.save()

        tr = cu("tracer", password="pulsebomb")
        tr.groups.add(s)
        tr.save()

        l = cu("lucio", password="soundbarrier")
        l.groups.add(s)
        l.save()

        aa = m.Course(id="F20AA", name="test course for AA")
        aa.save()
        bb = m.Course(id="F20BB", name="test course for BB")
        bb.save()
        cc = m.Course(id="F20CC", name="test course CC with no students")
        cc.save()

        eu1 = m.EnrolledUser(login=w, course=aa)
        eu1.save()
        eu2 = m.EnrolledUser(login=z, course=bb)
        eu2.save()
        eu3 = m.EnrolledUser(login=sy, course=cc)
        eu3.save()
        eu4 = m.EnrolledUser(login=a, course=aa)
        eu4.save()
        eu5 = m.EnrolledUser(login=a, course=bb)
        eu5.save()
        eu6 = m.EnrolledUser(login=tr, course=bb)
        eu6.save()
        eu7 = m.EnrolledUser(login=l, course=aa)
        eu7.save()

        cwa1 = m.Coursework(name="defend the objective",
                            descriptor="http://uni.lonm.uk/example_aa1.pdf",
                            course=aa,
                            state=m.Coursework.SOL_ONLY)
        cwa1.save()
        cwa2 = m.Coursework(name="students cant see this one yet",
                            descriptor="http://uni.lonm.uk/example_aa2.pdf",
                            course=aa,
                            state=m.Coursework.INVISIBLE)
        cwa2.save()
        cwa3 = m.Coursework(name="attack the objective",
                            descriptor="http://uni.lonm.uk/example_aa3.pdf",
                            course=aa,
                            state=m.Coursework.CLOSED)
        cwa3.save()
        cwb1 = m.Coursework(name="deliver the payload",
                            descriptor="http://uni.lonm.uk/example_bb1.pdf",
                            course=bb,
                            state=m.Coursework.SOL_ONLY)
        cwb1.save()
        cwb2 = m.Coursework(name="secure the payload",
                            descriptor="http://uni.lonm.uk/example_bb2.pdf",
                            course=bb,
                            state=m.Coursework.CLOSED)
        cwb2.save()
        cwc1 = m.Coursework(name="no-one can see this except teacher for cc",
                            descriptor="http://uni.lonm.uk/example_cc1.pdf",
                            course=cc,
                            state=m.Coursework.INVISIBLE)
        cwc1.save()

        return HttpResponse("DB populated")
    else:
        return HttpResponseForbidden()
