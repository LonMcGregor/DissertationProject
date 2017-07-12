from django.db import transaction

import common.models as m
import feedback.models as fm


@transaction.atomic()
def create_peer_test(solution, test, cw, feedback_group, initiator):
    """Create a new test match with data specified by the IDs of @solution,
    @test, @feedback_group and the instance of @cw, @initiator"""
    if solution == 'O' and test == 'S':
        raise Exception("Either test, solution or both need to be a student upload")
    group = fm.FeedbackGroup.objects.get(id=feedback_group)
    if solution != 'O':
        solution = m.Submission.objects.get(id=solution, coursework=cw,
                                             type=m.SubmissionType.SOLUTION)
        if not fm.FeedbackMembership.objects.filter(group=group, user=solution.creator).exists():
            raise Exception("That solution is not included in your feedback group")
    else:
        solution = m.Submission.objects.get(coursework=cw,
                                            type=m.SubmissionType.ORACLE_EXECUTABLE)
    if test != 'S':
        test_case = m.Submission.objects.get(id=test, creator=initiator, coursework=cw,
                                             type=m.SubmissionType.TEST_CASE)
    else:
        test_case = m.Submission.objects.get(coursework=cw,
                                             type=m.SubmissionType.SIGNATURE_TEST)
    new_tm = m.TestMatch(id=m.new_random_slug(m.TestMatch),
                         test=test_case,
                         test_version=test_case.latest_version,
                         solution=solution,
                         solution_version=solution.latest_version,
                         coursework=cw,
                         type=m.TestType.PEER)
    new_tm.save()
    fm.TestAccessControl(test=new_tm, group=group, initiator=initiator).save()
    return new_tm


@transaction.atomic()
def create_teacher_test(solution, test, cw):
    """Create a new test match with data specified by the IDs of @solution,
    @test, and @cw instanceand create the teachers test"""
    solution = m.Submission.objects.get(id=solution, coursework=cw)
    test_case = m.Submission.objects.get(id=test, coursework=cw)
    new_tm = m.TestMatch(id=m.new_random_slug(m.TestMatch),
                         test=test_case,
                         test_version=test_case.latest_version,
                         solution=solution,
                         solution_version=solution.latest_version,
                         coursework=cw,
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
    new_tm = m.TestMatch(id=m.new_random_slug(m.TestMatch),
                         test=test_case,
                         test_version=test_case.latest_version,
                         solution=solution,
                         solution_version=solution.latest_version,
                         coursework=coursework,
                         type=m.TestType.SELF)
    new_tm.save()
    return new_tm
