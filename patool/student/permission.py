"""A selection of helper methods designed to be used to check
whether or not a particular action should be carried out.
Methods in here should only ever READ, never WRITE"""

import student.models as m
from enum import Enum
from django.contrib.auth.models import Group
import student.helper as h


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


def user_feedback_mode(user, test_match_instance):
    """Return the status that the @user has in relation
    to a particular @test_data_instance wrt feedback"""
    cw = test_match_instance.coursework
    if not can_view_coursework(user, cw):
        return UserFeedbackModes.DENY
    if is_teacher(user):
        return UserFeedbackModes.READ
    if is_owner_of_solution(user, test_match_instance) or user == test_match_instance.initiator:
        return UserFeedbackModes.READ if test_match_instance.waiting_to_run else \
            UserFeedbackModes.WAIT
    if test_match_instance.marker != user:
        return UserFeedbackModes.DENY
    if test_match_instance.waiting_to_run:
        return UserFeedbackModes.WAIT
    return UserFeedbackModes.WRITE if test_match_instance.feedback is None else \
        UserFeedbackModes.READ


def can_view_file(user, file):
    """Determine if a @user should be allowed to view a given @file"""
    if not can_view_coursework(user, file.submission.coursework):
        return False
    if is_teacher(user):
        return True
    if file.submission.type == m.SubmissionType.CW_DESCRIPTOR:
        return True
    if user == file.submission.creator:
        return True
    if file.submission.private:
        return False
    test_containing_file = h.get_test_match_with_associated_submission(file.submission)
    if test_containing_file is None:
        return False
    if test_containing_file.marker == user:
        return True
    if test_containing_file.visible_to_developer:
        return True
    return False
