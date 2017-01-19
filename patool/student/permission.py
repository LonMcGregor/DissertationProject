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
    SOLUTION = 1
    TESTCASE = 2
    TESTWAIT = 3
    FEEDBACK = 4
    COMPLETE = 5


def state_of_user_in_coursework(user, coursework):
    """@user is a user model instance,
    @coursework is a coursework model instance
    determine where in the sequence of using
    the application a user is right now."""
    # todo this method relies on only one file per type per coursework
    if not can_view_coursework(user, coursework):
        return UserCourseworkState.NOACCESS
    files = m.File.objects.filter(coursework=coursework, creator=user)
    if files.filter(type=m.FileType.SOLUTION).count() != 1:
        return UserCourseworkState.SOLUTION
    if files.filter(type=m.FileType.TEST_CASE).count() != 1:
        return UserCourseworkState.TESTCASE
    test_data = h.get_test_data_for_tester(user, coursework)
    if test_data.waiting_to_run:
        return UserCourseworkState.TESTWAIT
    if not test_data.feedback:
        return UserCourseworkState.FEEDBACK
    return UserCourseworkState.COMPLETE


def user_can_upload_of_type(user, coursework, up_type):
    """For a given @user, within the scope of a @coursework,
    determine whether or not they are allowed to upload an @up_type file"""
    if up_type not in [m.FileType.SOLUTION, m.FileType.TEST_CASE]:
        return False
    state = state_of_user_in_coursework(user, coursework)
    if up_type == m.FileType.SOLUTION and state == UserCourseworkState.SOLUTION:
        return True
    if up_type == m.FileType.TEST_CASE and state == UserCourseworkState.TESTCASE:
        return True
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
    WAIT_TEST = 3
    WAIT_FEEDBACK = 4


def is_owner_of_solution(user, test_data_instance):
    """For a given @user, are they the owner of the solution
    in the @test_data_instance"""
    return test_data_instance.solution.creator == user


def user_feedback_mode(user, test_data_instance):
    """Return the status that the @user has in relation
    to a particular @test_data_instance wrt feedback"""
    cw = test_data_instance.coursework
    if not can_view_coursework(user, cw):
        return UserFeedbackModes.DENY
    if is_teacher(user):
        return UserFeedbackModes.READ
    if is_owner_of_solution(user, test_data_instance):
        if test_data_instance.feedback:
            return UserFeedbackModes.READ
        return UserFeedbackModes.WAIT_FEEDBACK
    if test_data_instance.initiator != user:
        return UserFeedbackModes.DENY
    if test_data_instance.waiting_to_run:
        return UserFeedbackModes.WAIT_TEST
    # todo currently do not allow changing of feedback.
    # todo could allow in future until status of cw set to closed
    if test_data_instance.feedback is None:
        return UserFeedbackModes.WRITE
    else:
        return UserFeedbackModes.READ


def can_view_file(user, file):
    """Determine if a @user should be allowed to view a given @file"""
    if not can_view_coursework(user, file.coursework):
        return False
    if is_teacher(user):
        return True
    if user == file.creator:
        return True
    test_containing_file = h.get_test_data_with_associated_file(file)
    if test_containing_file.test.creator == user:
        return True
    if test_containing_file.solution.creator == user and test_containing_file.feedback:
        return True
    return False
