from django.db import transaction
from django.contrib.auth.models import User

import student.models as m


@transaction.atomic()
def first_available(coursework, initiator, marker, visible):
    """This method will perform a matching of students.
    this generic method takes solutions and matches them
    to tests on a first-come basis - uses common arguments
    for testmatch objects: @initiator, @marker bool if needed,
    @visible to developer if needed"""
    cw = m.Coursework.objects.get(id=coursework)
    unassigned_solutions = list(m.Submission.objects.filter(coursework=cw,
                                                            type=m.SubmissionType.SOLUTION,
                                                            private=False, final=True))
    unassigned_tests = list(m.Submission.objects.filter(coursework=cw,
                                                        type=m.SubmissionType.TEST_CASE,
                                                        private=False, final=True))
    unassigned_users = list(m.EnrolledUser.objects.filter(course=cw.course))
    for sol in unassigned_solutions:
        chosen_test = None
        chosen_marker = None
        for test in unassigned_tests:
            if sol.creator != test.creator:
                chosen_test = test
                break
        if chosen_test is None:
            raise Exception("Not enough tests available to cover solutions")
        if marker:
            for user in unassigned_users:
                if sol.creator != user.login:
                    chosen_marker = user
                    break
        m.TestMatch(id=m.new_random_slug(m.TestMatch), test=chosen_test, solution=sol,
                    coursework=cw, initiator=initiator, waiting_to_run=True,
                    visible_to_developer=visible, marker=chosen_marker.login).save()
        unassigned_tests.remove(chosen_test)
        unassigned_users.remove(chosen_marker)


@transaction.atomic()
def create_single_test_match(solution, test, cw, marker, visible, initiator):
    """Create a new test match with data specified by the IDs of @solution,
    @test, @cw, @marker, @visible and the instance of @initiator user"""
    solution = m.Submission.objects.get(id=solution)
    test_case = m.Submission.objects.get(id=test)
    if solution.type != m.SubmissionType.SOLUTION or test_case.type != m.SubmissionType.TEST_CASE:
        raise Exception("Need 1 solution and 1 test")
    cw = m.Coursework.objects.get(id=cw)
    marker = User.objects.get(username=marker)
    if m.EnrolledUser.objects.filter(course=cw.course, login=marker).count() != 1:
        raise Exception("You're not allowed to edit this course")
    new_tm = m.TestMatch(id=m.new_random_slug(m.TestMatch), test=test_case, solution=solution,
                         coursework=cw, initiator=initiator, waiting_to_run=True,
                         visible_to_developer=visible,
                         marker=marker)
    new_tm.save()


@transaction.atomic()
def student_create_single_test_match(solution_id, test_id, cw_id, user):
    """Receive data to create a student-specific test match. Pass in IDs for
    @solution_id, @test_id, @cw_id and an @user instance. Return the newly created test"""
    coursework = m.Coursework.objects.get(id=cw_id)
    if 'solution' == '' and 'test' == '':
        raise Exception("Either test, solution or both need to be one of your uploads")
    if solution_id != '':
        solution = m.Submission.objects.get(id=solution_id, type=m.SubmissionType.SOLUTION)
        if solution.creator != user:
            raise Exception("At this stage you can only test your own uploads")
    else:
        solution = m.Submission.objects.get(coursework=coursework,
                                            type=m.SubmissionType.ORACLE_EXECUTABLE)
    if test_id != '':
        test_case = m.Submission.objects.get(id=test_id, type=m.SubmissionType.TEST_CASE)
        if test_case.creator != user:
            raise Exception("At this stage you can only test your own uploads")
    else:
        test_case = m.Submission.objects.get(coursework=coursework,
                                             type=m.SubmissionType.IDENTITY_TEST)
    new_tm = m.TestMatch(id=m.new_random_slug(m.TestMatch), test=test_case, solution=solution,
                         coursework=coursework, initiator=user, waiting_to_run=True,
                         visible_to_developer=True)
    new_tm.save()
    return new_tm

AVAILABLE_MATCHES = (('fa', first_available),)
