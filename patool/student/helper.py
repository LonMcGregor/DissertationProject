"""A selection of methods that offer help to some other
functionality of the program, but in and of themselves
do not actually offer services to views, permissions etc."""
from django.contrib.auth.models import Group

import student.models as m
import feedback.models as fm

from django.core.exceptions import ObjectDoesNotExist


def string_id(item):
    """Pass in a model instance @item and get the
    id back as a string, or '' if it was not instantiated """
    return str(item.id) if item is not None else ''


def first_model_item_or_none(query):
    """Working on the assumption that a user will only submit an item
    once in a given state, take the output of the @query, and give
    either the first item, or None"""
    if query.count() > 0:
        return query[0]
    return None


def test_match_for_results(submission):
    """Given that a results @submission only is ever attached to
    a single test match, we can return it"""
    return m.TestMatch.objects.get(result=submission)


def get_files(submission):
    """For a given @submission instance, get the
    names of the files back as an array"""
    files = m.File.objects.filter(submission=submission)
    list_files = []
    for file in files:
        list_files.append(file.file.name.split('/')[-1])
    return list_files


def delete_old_solution(user, cw_instance):
    """For a given @cw_instance, and a @user, delete the existing
    solution file if it exists as it is about to be replaced.
    By itself, this method is NOT ATOMIC"""
    sol_query = m.Submission.objects.filter(creator=user, coursework=cw_instance,
                                            type=m.SubmissionType.SOLUTION)
    solution = first_model_item_or_none(sol_query)
    if solution is not None:
        solution.delete()


def delete_submission(user, submission):
    """Given a @user and a @submission, see if the user
    is allowed to delete said submission, and carry out"""
    if submission.creator != user:
        return False
    if can_delete(submission):
        submission.delete()
        return True
    return False


def can_delete(submission):
    """Assuming that the owner of the @submission is verified,
    check that it can actually be deleted safely"""
    cw = submission.coursework
    if cw.state == m.CourseworkState.UPLOAD and submission.type == m.SubmissionType.TEST_CASE:
        return True
    if cw.state == m.CourseworkState.FEEDBACK and submission.type == m.SubmissionType.TEST_CASE \
            and m.TestMatch.objects.filter(test=submission).count == 0:
            return True
    return False


def get_feedback_groups_for_user_in_coursework(user, coursework):
    """Given @user trying to give feedback for @coursework
    get all of the groups they are assigned to as a list"""
    all_groups_in_cw = [p.group for p in fm.FeedbackPlan.objects.filter(coursework=coursework)]
    all_groups_for_user = [mb.group for mb in fm.FeedbackMembership.objects.filter(user=user)]
    return list(set(all_groups_for_user).intersection(all_groups_in_cw))


def get_all_users_in_feedback_group(group):
    """Given a feedback @group, determine all of the member users"""
    return [(member.user, member.nickname) for member in
            fm.FeedbackMembership.objects.filter(group=group)]


def get_all_test_matches_in_feedback_group(user, group):
    """"Given a feedback @group,
    get all of the associated test matches.
    personalise names for @user"""
    return [detail_test_match(user, item.test_match, item.group) for item in
            fm.FeedbackForTestMatch.objects.filter(group=group)]


def detail_test_match(user, tm, group):
    """Given a instance of a @user, a @tm and a
    feedback @group, get the details of names of
    the submission within the @tm as a triple"""
    if is_teacher(user):
        return tm, tm.solution.teacher_name, tm.test.teacher_name
    developer = fm.FeedbackMembership.objects.get(group=group, user=tm.solution.creator)
    sol_name = tm.solution.student_name if tm.solution.creator == user else \
        developer.nickname+tm.solution.peer_name
    tester = fm.FeedbackMembership.objects.get(group=group, user=tm.solution.creator)
    test_name = tm.test.student_name if tm.test.creator == user else \
        tester.nickname+tm.test.peer_name
    return tm, sol_name, test_name


def get_name_for_test_match(user, tm):
    """Get the names a a tuple for the submissions in a
    @tm instance, customised for @user"""
    group_query = fm.FeedbackForTestMatch.objects.filter(test_match=tm)
    group = first_model_item_or_none(group_query)
    if group is None:
        return tm.solution.student_name, tm.test.student_name
    else:
        triple = detail_test_match(user, tm, group.group)
        return triple[1], triple[2]


def feedback_group_for_test_match(tm):
    """Given a @tm, get the feedback group associated"""
    model = first_model_item_or_none(fm.FeedbackForTestMatch.objects.filter(test_match=tm))
    return model.group if model is not None else None


def count_members_of_group(group):
    """Count the number of members of specified feedback @group"""
    return fm.FeedbackMembership.objects.filter(group=group).count()


def get_descriptor_tuples(coursework):
    """Get the descriptors and files for @coursework"""
    [(s, get_files(s)) for s in m.Submission.objects.filter(
        type=m.SubmissionType.CW_DESCRIPTOR, coursework=coursework)]


def get_solution_tuples(coursework, user):
    """Get the solution submissions and files
    for @coursework by @user"""
    return [(s, get_files(s)) for s in
            m.Submission.objects.filter(coursework=coursework, creator=user,
                                        type=m.SubmissionType.SOLUTION)]


def get_test_triples(coursework, user):
    """Get the test submissions and files, and
    ability to delete for @coursework by @user"""
    return [(t, get_files(t), can_delete(t)) for t in m.Submission.objects.filter(
        coursework=coursework, creator=user, type=m.SubmissionType.TEST_CASE)]


def nick_for_user_in_group(user, group, requesting_user):
    """Find the nickname, and real name in brackets if
    @requesting_user is a teacher or the person being checked
    needed, for the specified @user in feedback @group"""
    try:
        nick = fm.FeedbackMembership.objects.get(group=group, user=user).nickname
        if requesting_user == user:
            return "Me (%s)" % nick
        if is_teacher(requesting_user):
            return "%s (%s)" % (nick, user.username)
        return nick
    except ObjectDoesNotExist:
        return "Unknown User - %s, %s" % user.id, group.id


def is_teacher(user):
    """is @user a teacher?"""
    teacher_group = Group.objects.get(name="teacher")
    return teacher_group in user.groups.all()