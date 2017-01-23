"""A selection of methods that offer help to some other
functionality of the program, but in and of themselves
do not actually offer services to views, permissions etc."""

import student.models as m


def string_id(item):
    """Pass in a model instance @item and get the
    id back as a string, or '' if it was not instantiated """
    return str(item.id) if item is not None else ''


def get_test_data_for_tester(user, coursework):
    """Get the test data for the tester @user, within a given @coursework"""
    return first_model_item_or_none(m.TestData.objects.filter(
        initiator=user, coursework=coursework))


def get_test_data_for_developer(user, coursework):
    """Get the test data for the developer @user, for given @coursework"""
    sol = user_submitted_file(user, coursework, m.FileType.SOLUTION)
    return first_model_item_or_none(m.TestData.objects.filter(
        coursework=coursework, solution=sol))


def get_feedback_for_solution(coursework, solution):
    """Get the feedback for the developer, based on a @coursework for a @solution"""
    return first_model_item_or_none(m.TestData.objects.filter(
        coursework=coursework, solution=solution))


def read_file_by_line(file):
    """Read back the contents of a @file as a string"""
    content = ""
    while True:
        buf = file.readline()
        content += buf.decode('utf-8')
        if buf == b'':
            return content


def user_submitted_file(user, coursework, file_type):
    """return the @file_type @user submitted for @coursework"""
    return first_model_item_or_none(m.File.objects.filter(
        coursework=coursework, creator=user, type=file_type))


def first_model_item_or_none(query):
    """Working on the assumption that a user will only submit an item
    once in a given state, take the output of the @query, and give
    either the first item, or None"""
    if query.count() > 0:
        return query[0]
    return None


def get_test_data_with_associated_file(file):
    """Given a certain @file within the scope of a @coursework,
    get the test data file that contains it. This assumes
    that a file will only be used once"""
    if file.type == m.FileType.SOLUTION:
        return first_model_item_or_none(m.TestData.objects.filter(solution=file))
    if file.type == m.FileType.TEST_CASE:
        return first_model_item_or_none(m.TestData.objects.filter(test=file))
    if file.type == m.FileType.TEST_RESULT:
        return first_model_item_or_none(m.TestData.objects.filter(results=file))
    if file.type == m.FileType.FEEDBACK:
        return first_model_item_or_none(m.TestData.objects.filter(feedback=file))
    raise Exception("You shouldn't have reached here")
