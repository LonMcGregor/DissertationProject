"""A selection of methods that offer help to some other
functionality of the program, but in and of themselves
do not actually offer services to views, permissions etc."""

import student.models as m


def string_id(item):
    """Pass in a model instance @item and get the
    id back as a string, or '' if it was not instantiated """
    return str(item.id) if item is not None else ''


def get_test_match_for_developing(user, coursework):
    """Get the test matches that @user created while in development of a solution for @coursework"""
    initiated = m.TestMatch.objects.filter(coursework=coursework, initiator=user)
    chosen = []
    for tm in initiated:
        if tm.solution.creator == user or tm.test.creator == user:
            chosen.append(tm)
    return chosen


def get_test_match_for_developer(user, coursework):
    """Get the test matches for the developer @user, for given @coursework"""
    visibles = m.TestMatch.objects.filter(coursework=coursework,
                                          visible_to_developer=True).exclude(initiator=user)
    chosen = []
    for tm in visibles:
        if tm.solution.creator == user:
            chosen.append(tm)
    return chosen


def read_file_by_line(file):
    """Read back the contents of a @file as a string"""
    content = ""
    while True:
        buf = file.readline()
        content += buf.decode('utf-8')
        if buf == b'':
            return content


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
    if submission.type in [m.SubmissionType.TEST_CASE, m.SubmissionType.IDENTITY_TEST]:
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


def get_file(submission_id, filename):
    """For a specified @submission_id, and @filename, get
    the file object associated with that"""
    sub = m.Submission.objects.get(id=submission_id)
    files = m.File.objects.filter(submission=sub)
    for file in files:
        if file.file.name.split('/')[-1] == filename:
            return file
    raise Exception("File not found")
