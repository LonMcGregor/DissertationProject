"""A selection of helper methods designed to be used to check
whether or not a particular action should be carried out.
Methods in here should only ever READ, never WRITE"""

from enum import Enum

from django.contrib.auth.models import Group

import student.helper as h
import student.models as m


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


def user_feedback_mode(user, test_match_instance):
    """Return the status that the @user has in relation
    to a particular @test_data_instance wrt feedback"""
    cw = test_match_instance.coursework
    if not can_view_coursework(user, cw):
        return UserFeedbackModes.DENY
    if is_teacher(user):
        return UserFeedbackModes.WRITE if user in [0, 1, 2] else \
            UserFeedbackModes.READ
    # that is to say, if the user is inside the feedback group (TODO)
    if is_owner_of_solution(user, test_match_instance) or \
            (test_match_instance.test.creator == user and
             test_match_instance.solution.type == m.SubmissionType.ORACLE_EXECUTABLE):
        return UserFeedbackModes.WAIT if test_match_instance.error_level is None else \
            UserFeedbackModes.READ
    if test_match_instance.marker != user:
        return UserFeedbackModes.DENY
    if test_match_instance.error_level is None:
        return UserFeedbackModes.WAIT
    return UserFeedbackModes.WRITE if (test_match_instance.feedback is None and
                                       test_match_instance.coursework.state ==
                                       m.CourseworkState.FEEDBACK) else UserFeedbackModes.READ


def can_view_file(user, file):
    """Determine if a @user should be allowed to view a given @file"""
    return can_view_submission(user, file.submission)


def can_view_submission(user, submission):
    """Determine is a @user is allowed to see a given submission"""
    if not can_view_coursework(user, submission.coursework):
        return False
    if is_teacher(user):
        return True
    if submission.type in [m.SubmissionType.CW_DESCRIPTOR, m.SubmissionType.SIGNATURE_TEST]:
        return True
    if submission.type == m.SubmissionType.ORACLE_EXECUTABLE:
        return False
    if user == submission.creator:
        return True
    test_containing_file = h.get_test_match_with_associated_submission(submission)
    if test_containing_file is None:
        return False
    # todo true if in testing group
    if (test_containing_file.test.type == m.SubmissionType.SIGNATURE_TEST and
        submission.type == m.SubmissionType.TEST_RESULT and
        test_containing_file.solution.creator == user):
        return True
    return False
