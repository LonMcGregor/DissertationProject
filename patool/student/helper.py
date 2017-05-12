"""A selection of methods that offer help to some other
functionality of the program, but in and of themselves
do not actually offer services to views, permissions etc."""

import student.models as m


def string_id(item):
    """Pass in a model instance @item and get the
    id back as a string, or '' if it was not instantiated """
    return str(item.id) if item is not None else ''


def first_model_item_or_none(query):
    """Working on the assumption that a user will only submit an item
    once in a given state, take the output of the @query, and give
    either the first item, or None"""
    if query.count() > 0:
        return query[0]
    return None


def get_test_match_with_associated_submission(submission):
    """Given a certain @submission within the scope of a,
    get the test data file that contains it. This assumes
    that a file will only be used once"""
    if submission.type in [m.SubmissionType.SOLUTION, m.SubmissionType.ORACLE_EXECUTABLE]:
        return first_model_item_or_none(m.TestMatch.objects.filter(solution=submission))
    if submission.type in [m.SubmissionType.TEST_CASE, m.SubmissionType.SIGNATURE_TEST]:
        return first_model_item_or_none(m.TestMatch.objects.filter(test=submission))
    if submission.type == m.SubmissionType.TEST_RESULT:
        return first_model_item_or_none(m.TestMatch.objects.filter(result=submission))
    if submission.type == m.SubmissionType.FEEDBACK:
        return first_model_item_or_none(m.TestMatch.objects.filter(feedback=submission))
    raise Exception("You shouldn't have reached here")


def get_files(submission):
    """For a given @submission instance, get the
    names of the files back as an array"""
    files = m.File.objects.filter(submission=submission)
    list_files = []
    for file in files:
        list_files.append(file.file.name.split('/')[-1])
    return list_files


def delete_old_solution(user, cw_instance):
    """For a given @cw_instance, and a @user, delete the existing
    solution file if it exists as it is about to be replaced.
    By itself, this method is NOT ATOMIC"""
    sol_query = m.Submission.objects.filter(creator=user, coursework=cw_instance,
                                            type=m.SubmissionType.SOLUTION)
    solution = first_model_item_or_none(sol_query)
    if solution is not None:
        solution.delete()


def delete_submission(user, submission):
    """Given a @user and a @submission, see if the user
    is allowed to delete said submission, and carry out"""
    if submission.creator != user:
        return False
    if can_delete(submission):
        submission.delete()
        return True
    return False


def can_delete(submission):
    """Assuming that the owner of the @submission is verified,
    check that it can actually be deleted safely"""
    cw = submission.coursework
    if cw.state == m.CourseworkState.UPLOAD and submission.type == m.SubmissionType.TEST_CASE:
        return True
    if cw.state == m.CourseworkState.FEEDBACK and submission.type == m.SubmissionType.TEST_CASE \
            and m.TestMatch.objects.filter(test=submission).count == 0:
            return True
    return False
