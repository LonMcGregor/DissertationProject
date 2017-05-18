"""A selection of helper methods designed to be used to check
whether or not a particular action should be carried out.
Methods in here should only ever READ, never WRITE"""

from enum import Enum

from django.contrib.auth.models import Group

import student.helper as h
import student.models as m
import feedback.models as fm


def coursework_available_for_user(user):
    """For a given @request, return a list of coursework available to the user"""
    enrolled_courses = m.EnrolledUser.objects.filter(login=user).values('course')
    courses_for_user = m.Course.objects.filter(code__in=enrolled_courses)
    all_courseworks_for_user = m.Coursework.objects.filter(course__in=courses_for_user)
    visible_courseworks = []
    for item in all_courseworks_for_user:
        if can_view_coursework(user, item):
            visible_courseworks.append((item.id, item.state, item.course.code, item.name))
    return visible_courseworks


def can_view_coursework(user, coursework):
    """BOOL: Check if the given @user instance is
    allowed to view the specified @coursework instance"""
    is_enrolled = m.EnrolledUser.objects.filter(login=user).filter(course=coursework.course)
    if is_enrolled.count() != 1:
        return False
    return True if is_teacher(user) else coursework.is_visible()


class UserCourseworkState(Enum):
    """Define which state a user is in in relation to a coursework
    e.g. what is the next item of input required from them"""
    NOACCESS = 0
    UPLOADS = 1
    FEEDBACK = 2
    COMPLETE = 3


def state_of_user_in_coursework(user, coursework):
    """@user is a user model instance,
    @coursework is a coursework model instance
    determine where in the sequence of using
    the application a user is right now."""
    if not can_view_coursework(user, coursework):
        return UserCourseworkState.NOACCESS
    if coursework.state == m.CourseworkState.UPLOAD:
        return UserCourseworkState.UPLOADS
    if coursework.state == m.CourseworkState.FEEDBACK:
        return UserCourseworkState.FEEDBACK
    return UserCourseworkState.COMPLETE


def user_can_upload_of_type(user, coursework, up_type):
    """For a given @user, within the scope of a @coursework,
    determine whether or not they are allowed to upload an @up_type file"""
    state = state_of_user_in_coursework(user, coursework)
    if state == UserCourseworkState.UPLOADS:
        return up_type in [m.SubmissionType.SOLUTION, m.SubmissionType.TEST_CASE]
    if state == UserCourseworkState.FEEDBACK:
        return up_type in [m.SubmissionType.TEST_CASE]
    return False


def is_teacher(user):
    teacher_group = Group.objects.get(name="teacher")
    return teacher_group in user.groups.all()


class UserFeedbackModes(Enum):
    """Enumerate possible actions a user has with regards
    to providing feedback on a test data instance. """
    DENY = 0
    READ = 1
    WRITE = 2
    WAIT = 3


def is_owner_of_solution(user, test_match_instance):
    """For a given @user, are they the owner of the solution
    in the @test_match_instance"""
    return test_match_instance.solution.creator == user


def user_is_self_testing(user, test_match_instance):
    """Check and return whether @user was involed in a
    self-test for @test_match_instance"""
    if test_match_instance.type != m.TestType.SELF:
        return False
    return test_match_instance.test.creator==user or test_match_instance.solution.creator == user


def user_is_member_of_test_match_feedback_group(user, test_match_instance):
    """Return whether or not a user is a member of the
    feedback group for a givne test match"""
    feedback_group_filter = fm.FeedbackForTestMatch.objects.filter(test_match=test_match_instance)
    feedback_group = h.first_model_item_or_none(feedback_group_filter)
    if feedback_group is None:
        return False
    return fm.FeedbackMembership.objects.filter(group=feedback_group, user=user).count() > 0


def state_given_error_level(test_match_instance, specified_mode):
    """Assuming a user is properly validated and
    allowed to see a @test_match_instance, determine if
    they should be in WAIT or @specified_mode"""
    if test_match_instance.error_level is None:
        return UserFeedbackModes.WAIT
    return specified_mode


def feedback_mode_given_coursework_state(test_match_instance):
    """Based on the current state of the coursework, determine if
    authorized users should be allowed to write feedback"""
    if test_match_instance.coursework.state == m.CourseworkState.FEEDBACK:
        return UserFeedbackModes.WRITE
    return UserFeedbackModes.READ


def user_feedback_mode(user, test_match_instance):
    """Return the status that the @user has in relation
    to a particular @test_match_instance wrt feedback"""
    cw = test_match_instance.coursework
    if not can_view_coursework(user, cw):
        return UserFeedbackModes.DENY
    if is_teacher(user):
        return UserFeedbackModes.READ
    if user_is_self_testing(user, test_match_instance):
        return state_given_error_level(test_match_instance, UserFeedbackModes.READ)
    if user_is_member_of_test_match_feedback_group(user, test_match_instance):
        mode = feedback_mode_given_coursework_state(test_match_instance)
        return state_given_error_level(test_match_instance, mode)
    return UserFeedbackModes.DENY


def can_view_file(user, file):
    """Determine if a @user should be allowed to view a given @file"""
    return can_view_submission(user, file.submission)


def submission_is_descriptive(submission):
    """Report if a @submission is a descriptive part of
    a coursework"""
    return submission.type in [m.SubmissionType.CW_DESCRIPTOR, m.SubmissionType.SIGNATURE_TEST]


def submission_is_secret(submission):
    """Report is a @submission is the kind that ought to be secret
    to students taking part in coursework"""
    return submission.type == m.SubmissionType.ORACLE_EXECUTABLE


def user_owns_submission(user, submission):
    """Return if @user is the owner of @submission,
    for example if they are the creator"""
    return user == submission.creator


def is_submission_written_by_peer_in_testing_group(user, submission):
    """Assuming there is a feedback group for the creator of @submission
    that the @user is trying to view, determine if this group in the
    coursework also includes @user"""
    submission_groups = [member.group for member in
                         fm.FeedbackMembership.objects.filter(user=submission.creator)]
    user_groups = [member.group for member in fm.FeedbackMembership.objects.filter(user=user)]
    common = list(set(submission_groups).intersection(user_groups))
    for group in common:
        if fm.FeedbackPlan.objects.filter(group=group,
                                          coursework=submission.coursework).count() == 1:
            return True
    return False


def is_visible_results_file(user, submission):
    """If the @submisison that @user is trying to  view is a
    results file, find the test it is from. If it is a self
    test for @user, let them see it. If they are in the testing
    group, let them see it"""
    if submission.type!=m.SubmissionType.TEST_RESULT:
        return False
    test_used_in = h.test_match_for_results(submission)
    return user_is_self_testing(user, test_used_in) or \
        user_is_member_of_test_match_feedback_group(user, test_used_in)


def can_view_submission(user, submission):
    """Determine is a @user is allowed to see a given submission"""
    if not can_view_coursework(user, submission.coursework):
        return False
    if is_teacher(user):
        return True
    if submission_is_descriptive(submission):
        return True
    if submission_is_secret(submission):
        return False
    if user_owns_submission(user, submission):
        return True
    if is_submission_written_by_peer_in_testing_group(user, submission):
        return True
    if is_visible_results_file(user, submission):
        return True
    return False
