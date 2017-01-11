"""A selection of helper methods designed to be used to check
whether or not a particular action should be carried out."""

import student.models as m
from enum import Enum


def can_view_coursework(user, coursework):
    """BOOL: Check if the given @user@ instance is
    allowed to view the specified @coursework@ instance"""
    is_enrolled = m.EnrolledUser.objects.filter(login=user).filter(course=coursework.course)
    if is_enrolled.count() != 1:
        return False
    return coursework.is_visible()


def can_upload_file(user, coursework, upload_type):
    """based on the @user instance and @coursework instance,
    determine if a user can upload a f... wait what?"""
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


class UserCourseworkState(Enum):
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
    the application a user is right now"""
    # todo note that this may be a temp setup to facilitate evaluation
    if not can_view_coursework(user, coursework):
        return UserCourseworkState.NOACCESS
    files = m.File.objects.filter(coursework=coursework).filter(creator=user)
    if files.filter(type=m.FileType.SOLUTION).count() != 1:
        return UserCourseworkState.SOLUTION
    tests = files.filter(type=m.FileType.TEST_CASE)
    if tests.count() == 0:
        return UserCourseworkState.TESTCASE
    # todo for now just use first found test - may wish to extend at future date to support multiple
    test = tests[0]
    results = m.TestResult.objects.filter(coursework=coursework).filter(test=test)
    result = results[0]
    if result.waiting_to_run:
        return UserCourseworkState.TESTWAIT
    if not result.feedback:
        return UserCourseworkState.FEEDBACK
    return UserCourseworkState.COMPLETE


def user_can_upload_of_type(user, coursework, up_type):
    if up_type not in [m.FileType.SOLUTION, m.FileType.TEST_CASE, m.FileType.FEEDBACK]:
        return False
    state = state_of_user_in_coursework(user, coursework)
    if up_type == m.FileType.SOLUTION and state == UserCourseworkState.SOLUTION:
        return True
    if up_type == m.FileType.TEST_CASE and state == UserCourseworkState.TESTCASE:
        return True
    if up_type == m.FileType.FEEDBACK and state == UserCourseworkState.FEEDBACK:
        return True
    return False


def user_submitted_solution(user, coursework):
    """return None if @user hasnt submitted a
    solution for @coursework else give the solution"""
    files = m.File.objects.filter(coursework=coursework).filter(
        creator=user).filter(type=m.FileType.SOLUTION)
    if files.count() > 0:
        return files[0]
    return None


def user_test_case(user, coursework):
    """return None if @user has not submitted a test case for
    @coursework, else give this test case"""
    files = m.File.objects.filter(coursework=coursework).filter(
        creator=user).filter(type=m.FileType.TEST_CASE)
    if files.count() > 0:
        return files[0]
    return None


def user_test_result(test_case):
    # todo currently this all acts assuming a test case is used once. fix this
    test_results = m.TestResult.objects.filter(test=test_case)
    if test_results.count() > 0:
        return test_results[0]
    return None


def user_feedback_for_solution(solution):
    # todo again assuming you will only ever get 1 feedbacks
    feedbacks = m.TestResult.objects.filter(solution=solution)
    if feedbacks.count() > 0:
        return feedbacks[0].feedback
    return None
