from django.http import HttpResponseForbidden
from django.contrib.auth.models import Group


def is_teacher(f):
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
