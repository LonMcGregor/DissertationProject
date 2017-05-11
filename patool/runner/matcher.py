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
def create_peer_test(solution, test, cw, created_by_teacher=False):
    """Create a new test match with data specified by the IDs of @solution,
    @test, @cw, @marker, @visible and the instance of @initiator user"""
    solution = m.Submission.objects.get(id=solution)
    test_case = m.Submission.objects.get(id=test)
    if solution.type != m.SubmissionType.SOLUTION or test_case.type != m.SubmissionType.TEST_CASE:
        raise Exception("Need 1 solution and 1 test")
    cw = m.Coursework.objects.get(id=cw)
    new_tm = m.TestMatch(id=m.new_random_slug(m.TestMatch), test=test_case,
                         solution=solution, coursework=cw,
                         type=m.TestType.TEACHER if created_by_teacher else m.TestType.PEER)
    # todo probably want to plug some sort of proxy in here for the feedback
    new_tm.save()


@transaction.atomic()
def create_self_test(solution_id, test_id, coursework, user):
    """Receive data to create a student-specific test match. Pass in IDs for
    @solution_id, @test_id and a @cw, @user instance. Return the newly created test."""
    if 'solution' == 'O' and 'test' == 'I':
        raise Exception("Either test, solution or both need to be one of your uploads")
    if solution_id != 'O':
        solution = m.Submission.objects.get(id=solution_id, creator=user,
                                            type=m.SubmissionType.SOLUTION)
    else:
        solution = m.Submission.objects.get(coursework=coursework,
                                            type=m.SubmissionType.ORACLE_EXECUTABLE)
    if test_id != 'I':
        test_case = m.Submission.objects.get(id=test_id, creator=user,
                                             type=m.SubmissionType.TEST_CASE)
    else:
        test_case = m.Submission.objects.get(coursework=coursework,
                                             type=m.SubmissionType.SIGNATURE_TEST)
    new_tm = m.TestMatch(id=m.new_random_slug(m.TestMatch), test=test_case, solution=solution,
                         coursework=coursework, type=m.TestType.SELF)
    new_tm.save()
    return new_tm

AVAILABLE_MATCHES = (('fa', first_available),)
