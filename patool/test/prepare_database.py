
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db import transaction
from common import models as m


@transaction.atomic
def prepare_database():
    """Populate the database with some testing data.
    Creates some teacher, some students, and some coursework tasks"""
    if not settings.DEBUG:
        print("Can only prepare test database when in debug mode")
        return

    User.objects.create_superuser(username='admin',
                                  email='admin@local.host',
                                  password='overwatch')

    t = Group()
    t.name = "teacher"
    t.save()
    s = Group()
    s.name = "student"
    s.save()
    fem = Group()
    fem.name = "female"
    fem.save()
    mal = Group()
    mal.name = "male"
    mal.save()
    edi = Group()
    edi.name = "edinburgh"
    edi.save()
    dub = Group()
    dub.name = "dubai"
    dub.save()

    cu = User.objects.create_user

    w = cu("winston", password="primalrage", email='winston@peer-testing.com')
    w.groups.add(t)
    w.save()
    z = cu("zenyatta", password="transcendence", email='zenyatta@peer-testing.com')
    z.groups.add(t)
    z.save()
    sy = cu("symmetra", password="teleporter", email='symmetra@peer-testing.com')
    sy.groups.add(t)
    sy.save()

    a = cu("ana", password="nanoboost", email='ana@peer-testing.com')
    a.groups.add(s)
    a.save()
    tr = cu("tracer", password="pulsebomb", email='tracer@peer-testing.com')
    tr.groups.add(s)
    tr.save()
    l = cu("lucio", password="soundbarrier", email='lucio@peer-testing.com')
    l.groups.add(s)
    l.save()
    sm = cu("sombra", password="electromagneticpulse", email='sombra@peer-testing.com')
    sm.groups.add(s)
    sm.save()

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
    m.EnrolledUser(login=sm, course=aa).save()
