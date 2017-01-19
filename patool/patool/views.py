from django.shortcuts import render
from django.db import transaction
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
from django.contrib.auth.models import User, Group
from student import models as m


def default_index(request):
    """Show a basic index page for the application"""
    return render(request, 'registration/landing.html')


@transaction.atomic
def populate_database(request):
    """Populate the database with some testing data.
    Creates some teacher, some students, and some coursework tasks"""
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
        l = cu("sombra", password="electromagneticpulse")
        l.groups.add(s)
        l.save()

        aa = m.Course(code="F20AA-2016_17", name="Advanced Algorithms")
        aa.save()
        bb = m.Course(code="F20BB-2016_17", name="Building Blocks")
        bb.save()
        cc = m.Course(code="F20CC-2016_17", name="Code Classes")
        cc.save()

        m.EnrolledUser(login=w, course=aa).save()
        m.EnrolledUser(login=z, course=bb).save()
        m.EnrolledUser(login=sy, course=cc).save()

        m.EnrolledUser(login=a, course=aa).save()
        m.EnrolledUser(login=tr, course=aa).save()
        m.EnrolledUser(login=l, course=aa).save()
        m.EnrolledUser(login=l, course=aa).save()

        m.Coursework(name="Build a binary tree",
                     descriptor="http://uni.lonm.uk/example_aa1.pdf",
                     course=aa,
                     state=m.CourseworkState.SOLUTIONS_ONLY).save()

        return HttpResponse("DB populated")
    else:
        return HttpResponseForbidden()
