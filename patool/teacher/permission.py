from django.contrib.auth.models import Group
from django.http import HttpResponseForbidden

import student.models as m


def is_teacher(f):
    """Mixin to prevent pages from being viewed if the
    currently logged in user is not in the teacher group.
    Passes rest of args on as a dictionary"""
    def is_teacher_internal(request, **args):
        teacher_group = Group.objects.get(name="teacher")
        if teacher_group in request.user.groups.all():
            if not args:
                return f(request)
            else:
                return f(request, args)
        else:
            return HttpResponseForbidden()

    return is_teacher_internal


def is_enrolled_on_course(user, course):
    is_enrolled = m.EnrolledUser.objects.filter(login=user).filter(course=course)
    return is_enrolled.count() == 1
