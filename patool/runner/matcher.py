from django.db import transaction

import student.models as m
import feedback.models as fm


@transaction.atomic()
def create_peer_test(solution, test, cw, feedback_group):
    """Create a new test match with data specified by the IDs of @solution,
    @test, @feedback_group and the instance of @cw test is done within"""
    solution = m.Submission.objects.get(id=solution)
    test_case = m.Submission.objects.get(id=test)
    group = fm.FeedbackGroup.objects.get(id=feedback_group)
    if solution.type != m.SubmissionType.SOLUTION or test_case.type != m.SubmissionType.TEST_CASE:
        raise Exception("Need 1 solution and 1 test")
    new_tm = m.TestMatch(id=m.new_random_slug(m.TestMatch), test=test_case,
                         solution=solution, coursework=cw,
                         type=m.TestType.PEER)
    new_tm.save()
    fm.FeedbackForTestMatch(test_match=new_tm, group=group).save()
    return new_tm


@transaction.atomic()
def create_teacher_test(solution, test, cw):
    """Create a new test match with data specified by the IDs of @solution,
    @test, and @cw instanceand create the teachers test"""
    solution = m.Submission.objects.get(id=solution)
    test_case = m.Submission.objects.get(id=test)
    new_tm = m.TestMatch(id=m.new_random_slug(m.TestMatch), test=test_case,
                         solution=solution, coursework=cw,
                         type=m.TestType.TEACHER)
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
