from django.shortcuts import render
from django.db import transaction
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
from django.contrib.auth.models import User, Group
from student import models as m


def default_index(request):
    return render(request, 'registration/landing.html')


@transaction.atomic
def populate_database(request):
    if settings.DEBUG:

        User.objects.create_superuser(username='admin',
                              email='admin@local.host',
                              password='overwatch')

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

        aa = m.Course(code="F20AA-2016_17", name="test course for AA")
        aa.save()
        bb = m.Course(code="F20BB-2016_17", name="test course for BB")
        bb.save()
        cc = m.Course(code="F20CC-2016_17", name="test course CC with no students")
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
                            state=m.CourseworkState.SOLUTIONS_ONLY)
        cwa1.save()
        cwa2 = m.Coursework(name="students cant see this one yet",
                            descriptor="http://uni.lonm.uk/example_aa2.pdf",
                            course=aa,
                            state=m.CourseworkState.INVISIBLE)
        cwa2.save()
        cwa3 = m.Coursework(name="attack the objective",
                            descriptor="http://uni.lonm.uk/example_aa3.pdf",
                            course=aa,
                            state=m.CourseworkState.CLOSED)
        cwa3.save()
        cwb1 = m.Coursework(name="deliver the payload",
                            descriptor="http://uni.lonm.uk/example_bb1.pdf",
                            course=bb,
                            state=m.CourseworkState.SOLUTIONS_ONLY)
        cwb1.save()
        cwb2 = m.Coursework(name="secure the payload",
                            descriptor="http://uni.lonm.uk/example_bb2.pdf",
                            course=bb,
                            state=m.CourseworkState.CLOSED)
        cwb2.save()
        cwc1 = m.Coursework(name="no-one can see this except teacher for cc",
                            descriptor="http://uni.lonm.uk/example_cc1.pdf",
                            course=cc,
                            state=m.CourseworkState.INVISIBLE)
        cwc1.save()

        return HttpResponse("DB populated")
    else:
        return HttpResponseForbidden()
