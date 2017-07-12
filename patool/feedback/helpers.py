from django.core.exceptions import ObjectDoesNotExist

import feedback.models as m
from common.permissions import is_teacher


def nick_for_user_in_group(user, group, requesting_user):
    """Find the nickname, and real name in brackets if
    @requesting_user is a teacher or the person being checked
    needed, for the specified @user in feedback @group"""
    try:
        nick = m.FeedbackMembership.objects.get(group=group, user=user).nickname
        if requesting_user == user:
            return "Me"
        if is_teacher(requesting_user):
            return "%s (%s)" % (nick, user.username)
        return nick
    except ObjectDoesNotExist:
        return "Unknown User - %s, %s" % user.id, group.id


def get_feedback_groups_for_user_in_coursework(user, coursework):
    """Given @user trying to give feedback for @coursework
    get all of the groups they are assigned to as a list"""
    return [mb.group for mb in m.FeedbackMembership.objects.filter(user=user)
            if mb.group.coursework == coursework]


def get_all_users_in_feedback_group(group):
    """Given a feedback @group, determine all of the member users"""
    return [(member.user, member.nickname) for member in
            m.FeedbackMembership.objects.filter(group=group)]


def get_all_test_matches_in_feedback_group(user, group):
    """"Given a feedback @group,
    get all of the associated test matches
    that @user should be able to access"""
    return [detail_test_match(user, tac.test, tac.group) for tac in
            m.TestAccessControl.objects.filter(group=group) if
            tac.initiator == user or tac.test.solution.creator == user]


def detail_test_match(user, tm, group):
    """Given a instance of a @user, a @tm and a
    feedback @group, get the details of names of
    the submission within the @tm as a triple"""
    if is_teacher(user):
        return tm, tm.solution.teacher_name, tm.test.teacher_name
    if is_teacher(tm.solution.creator):
        sol_name = tm.solution.student_name
    else:
        developer = m.FeedbackMembership.objects.get(group=group, user=tm.solution.creator)
        sol_name = tm.solution.student_name if tm.solution.creator == user else \
            developer.nickname+tm.solution.peer_name
    if is_teacher(tm.test.creator):
        test_name = tm.test.student_name
    else:
        tester = m.FeedbackMembership.objects.get(group=group, user=tm.test.creator)
        test_name = tm.test.student_name if tm.test.creator == user else \
            tester.nickname+tm.test.peer_name
    return tm, sol_name, test_name


def get_name_for_test_match(user, tm):
    """Get the names as a tuple for the submissions in a
    @tm instance, customised for @user"""
    group_query = m.TestAccessControl.objects.filter(test=tm)
    if not group_query.exists():
        return tm.solution.student_name, tm.test.student_name
    else:
        triple = detail_test_match(user, tm, group_query.first().group)
        return triple[1], triple[2]


def count_members_of_group(group):
    """Count the number of members of specified feedback @group"""
    return m.FeedbackMembership.objects.filter(group=group).count()


def feedback_group_for_test_match(tm):
    """Given a @tm, get the feedback group associated"""
    grouping = m.TestAccessControl.objects.filter(test=tm)
    return grouping.first().group if grouping.exists() else None

def user_is_member_of_group(user, group_id):
    """Given a @user and a @group_id, determine if membership exists"""
    group = m.FeedbackGroup.objects.get(id=group_id)
    return m.FeedbackMembership.objects.filter(group=group, user=user).exists()
