from django.db import transaction

import student.models as m


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
    return new_tm


@transaction.atomic()
def create_self_test(solution_id, test_id, coursework, user):
    """Receive data to create a student-specific test match. Pass in IDs for
    @solution_id, @test_id and a @cw, @user instance. Return the newly created test."""
    if solution_id == 'O' and test_id == 'S':
        raise Exception("Either test, solution or both need to be one of your uploads")
    if solution_id != 'O':
        solution = m.Submission.objects.get(id=solution_id, creator=user,
                                            type=m.SubmissionType.SOLUTION)
    else:
        solution = m.Submission.objects.get(coursework=coursework,
                                            type=m.SubmissionType.ORACLE_EXECUTABLE)
    if test_id != 'S':
        test_case = m.Submission.objects.get(id=test_id, creator=user,
                                             type=m.SubmissionType.TEST_CASE)
    else:
        test_case = m.Submission.objects.get(coursework=coursework,
                                             type=m.SubmissionType.SIGNATURE_TEST)
    new_tm = m.TestMatch(id=m.new_random_slug(m.TestMatch), test=test_case, solution=solution,
                         coursework=coursework, type=m.TestType.SELF)
    new_tm.save()
    return new_tm
