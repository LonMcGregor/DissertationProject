from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db import transaction
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render

from student import models as m

import subprocess

def default_index(request):
    """Show a basic index page for the application"""
    return render(request, 'registration/landing.html')


def ufs(request):
    for dir in ["uploads","tmp"]:
        args = "setfacl -Rm u:lm356:rwx var/%s" % dir
        proc = subprocess.run(args, cwd="/home/cs4/lm356/peer-testing",
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              universal_newlines=True, shell=True)
    return HttpResponse()


@transaction.atomic
def populate_database(request):
    """Populate the database with some testing data.
    Creates some teacher, some students, and some coursework tasks"""
    if settings.DEBUG:

        User.objects.create_superuser(username='apache@macs.hw.ac.uk',
                                      email='apache@macs.hw.ac.uk',
                                      password='the future is now thanks to science')

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

        l = cu("lm356@macs.hw.ac.uk", password="the future is now thanks to science")
        l.groups.add(t)
        l.save()

        lm = cu("lm356@hw.ac.uk", password="the future is now thanks to science")
        lm.groups.add(s)
        lm.groups.add(edi)
        lm.groups.add(mal)
        lm.save()

        return HttpResponse("DB populated")
    else:
        return HttpResponseForbidden()
