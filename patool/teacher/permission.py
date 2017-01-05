from django.http import HttpResponseForbidden
from django.contrib.auth.models import User, Group


def is_teacher(f):
    teacher_group = Group.objects.get(name="teacher")
    def is_teacher_internal(request):
        print(request.user.groups.all())
        if teacher_group in request.user.groups.all():
            return f(request)
        else:
            return HttpResponseForbidden()

    return is_teacher_internal
