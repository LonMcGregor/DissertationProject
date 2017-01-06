from django.http import HttpResponseForbidden
from django.contrib.auth.models import User, Group


def is_teacher(f):
    teacher_group = Group.objects.get(name="teacher")

    def is_teacher_internal(request, **args):
        if teacher_group in request.user.groups.all():
            if not args:
                return f(request)
            else:
                return f(request, args)
        else:
            return HttpResponseForbidden()

    return is_teacher_internal
