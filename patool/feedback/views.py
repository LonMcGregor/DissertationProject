from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest

import common.models as cm
from . import forms as f
from . import models as m
from common.permissions import require_teacher
import common.permissions as p

# TODO this stuff should really be a part of teacher...


@login_required()
@require_teacher
def modify(request):
    if request.method != "POST":
        return HttpResponseForbidden("You're only allowed to post stuff here")
    form = f.FeedbackGroupForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest("This form is not valid")
    coursework = cm.Coursework.objects.get(id=form.cleaned_data['coursework'])
    if not p.is_enrolled_on_course(request.user, coursework.course):
        return HttpResponseForbidden("You're not enrolled on the course")
    if form.cleaned_data['groupid'] == '':
        group = save_new_feedback_group(form.cleaned_data)
        associate_with_coursework(group, coursework)
        return HttpResponse("Group Added: " + str(group.id))
    else:
        group = m.FeedbackGroup.objects.get(id=form.cleaned_data['groupid'])
        modify_existing_feedback_group(group, form.cleaned_data)
        return HttpResponse("Group Modified: " + str(group.id))


@transaction.atomic()
def save_new_feedback_group(new_data):
    """save and return a new instance of a feedback group model
    and populate with the @new_data dictionary. Note:
    This method does no validation of if a user is enrolled on
    a course, as we may wish to be able to re-use these
    groups across courses"""
    group = m.FeedbackGroup(nickname=new_data["nickname"])
    group.save()
    count = 1
    new_students = new_data['students'].strip().strip(',').split(',')
    new_students_list = list(map(lambda w: w.strip(), new_students))
    for student in new_students_list:
        m.FeedbackMembership(group=group,
                             user=User.objects.get(username=student),
                             nickname="Peer #%s" % str(count)).save()
        count += 1
    return group


@transaction.atomic()
def associate_with_coursework(feedback_group, coursework):
    """Associate @feedback_group with @coursework"""
    m.FeedbackPlan(group=feedback_group, coursework=coursework).save()


@transaction.atomic()
def modify_existing_feedback_group(feedback_group, new_data):
    """Given an already existing @feedback_group, and some
    @new_data, go through this and update accordingly"""
    feedback_group.nickname = new_data['nickname']
    feedback_group.save()

    new_students = new_data['student'].strip().strip(',').split(',')
    new_students_list = list(map(lambda w: w.strip(), new_students))

    members = m.FeedbackMembership.objects.filter(group=feedback_group)
    count = members.count()
    for member in members:
        if str(member.login) not in new_students_list:
            member.delete()
    for member in new_students_list:
        current_user = m.User.objects.get(username=member)
        exists = m.FeedbackMembership.objects.filter(user=current_user, group=feedback_group)
        if exists.count() != 1:
            m.FeedbackMembership(user=current_user,
                                 group=feedback_group,
                                 nickname="Peer #%s" % str(count)).save()
            count += 1


@login_required()
@require_teacher
@transaction.atomic()
def delete(request):
    if request.method != "POST":
        return HttpResponseForbidden("You're only allowed to post stuff here")
    form = f.FeedbackGroupForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest("This form is not valid")
    coursework = cm.Coursework.objects.get(id=form.cleaned_data['coursework'])
    if not p.is_enrolled_on_course(request.user, coursework.course):
        return HttpResponseForbidden("You're not enrolled on the course")
    if form.cleaned_data['groupid'] is None:
        return HttpResponse("Group Doesn't Exist - No Action Taken")
    m.FeedbackGroup.objects.get(id=form.cleaned_data['groupid']).delete()
    return HttpResponse("Group Deleted")
