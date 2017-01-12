from django.conf import settings
import student.models as m
import sys
import subprocess
from django.core.files import File
from django.db import transaction
import time
import os


@transaction.atomic
def run_test(test_data_instance):
    solution_file = test_data_instance.solution.filepath
    test_path = test_data_instance.test.filepath
    if sys.platform == "linux":
        test_file = test_path.split('/')[::-1][0]
        script = '../../testrunner/tr'
    elif sys.platform == "win32":
        test_file = test_path.split('\\')[::-1][0]
        script = '..\\..\\testrunner\\tr.cmd'
    else:
        raise Exception("unsupported operating system")
    test_result_file = 'results' + str(time.time())
    test_dir = test_path[:len(test_file)]
    result = subprocess.run([script, solution_file, test_dir,
                    test_file, settings.TEST_RESULT_ROOT, test_result_file])
    result_file_instance = File(open(os.path.join(test_dir, test_result_file)))
    result_file = m.File(filepath=result_file_instance, coursework=test_data_instance.coursework,
                         creator=test_data_instance.user, type=m.FileType.TEST_RESULT)
    result_file.save()
    test_data_instance.results = result_file
    test_data_instance.error_level = result
    test_data_instance.waiting_to_run = False
    test_data_instance.save()


def get_next_unassigned_item(coursework, file_type, user):
    """for a given @coursework, get the next unassigned
    item, if any. Exclude items created by the @user
    who will be using this item"""
    items = m.File.objects.filter(coursework=coursework, type=file_type).exclude(creator=user)
    for item in items:
        kwargs = {"coursework": coursework}
        if file_type == m.FileType.SOLUTION:
            kwargs["solution"] = item
        elif file_type == m.FileType.TEST_CASE:
            kwargs["test"] = item
        else:
            raise Exception("bad arguments")
        if m.TestData.objects.filter(**kwargs).count() == 0:
            return item
    return None


@transaction.atomic
def new_item_uploaded(user, coursework, item, item_type):
    """a new @item @type file has been uploaded by @user and needs to be assigned
    to a test data run in order to get results for completing a @coursework"""
    if item_type == m.FileType.SOLUTION:
        match = m.FileType.TEST_CASE
    elif item_type == m.FileType.TEST_CASE:
        match = m.FileType.SOLUTION
    else:
        raise Exception("invalid type")
    matching_item = get_next_unassigned_item(coursework, match, user)
    if matching_item is None:
        return
    if item_type == m.FileType.SOLUTION:
        details = {'solution': item, 'test': matching_item}
    elif item_type == m.FileType.TEST_CASE:
        details = {'solution': matching_item, 'test': item}
    else:
        raise Exception("invalid type")
    tr = m.TestData(coursework=coursework, initiator=user, **details)
    tr.save()

    # todo call to test runner to start going through run queue
    # todo   this needs to be done in such a way if it is already
    # todo   running we don't restart it
    # todo !! if this method is trans atomic, we cant call the starter from here


def run_queued_tests():
    """go through all of the test data instances that are
    tagged as waiting to run, and run them"""
    while True:
        tests = m.TestData.objects.filter(waiting_to_run=True)
        if tests.count() == 0:
            return
        for test in tests:
            run_test(test)
