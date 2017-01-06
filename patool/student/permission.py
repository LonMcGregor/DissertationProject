"""A selection of helper methods designed to be used to check
whether or not a particular action should be carried out."""

import student.models as m
from django.http import Http404


def can_view_coursework(user, coursework):
    """BOOL: Check if the given @user@ is
    allowed to view the specified @coursework@"""
    is_enrolled = m.EnrolledUser.objects.filter(login=user).filter(course=coursework.course)
    if is_enrolled != 1:
        return False
    return coursework.is_visible()


def can_upload_file(user, coursework, upload_type):
    if not can_view_coursework(user, coursework):
        return False
    if upload_type == m.FileType.SOLUTION:
        pass
    elif upload_type == m.FileType.TEST_CASE:
        pass
    elif upload_type == m.FileType.TEST_RESULT:
        pass
    elif upload_type == m.FileType.FEEDBACK:
        pass
    else:
        return False


def cw_exists_for_upload(fun):
    def cw_exists_internal(request, singlecw):
        no_cws = m.Coursework.objects.filter(id=singlecw).count() != 1
        if singlecw is None or singlecw == "" or no_cws:
            return Http404()
        else:
            return fun(request, singlecw)
    return cw_exists_internal
