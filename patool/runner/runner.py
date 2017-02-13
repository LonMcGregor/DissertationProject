import os
import shutil
import subprocess
import sys
import threading

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction

import student.models as m

"""This module implements the execution mechanism with
respect to python3 unit testing."""


@transaction.atomic
def run_test(test_match_instance, exec_method):
    """Go through the @test_data_instance and run the
    test case against the solution. Store the data setting
    the results to be created by the initiator (which will
     likely be the test creator). Then update the database.
     Utilize the given @exec_method"""
    if not test_match_instance.waiting_to_run:
        return
    result, output = exec_method(test_match_instance.solution, test_match_instance.test)
    result_sub = m.Submission(id=m.new_random_slug(m.Submission),
                              coursework=test_match_instance.coursework,
                              creator=test_match_instance.initiator,
                              type=m.SubmissionType.TEST_RESULT,
                              private=test_match_instance.solution.private or
                                      test_match_instance.test.private)
    result_sub.save()
    result_file = m.File(submission=result_sub)
    result_file.file.save('results.txt', ContentFile(output))
    result_file.save()
    test_match_instance.result = result_sub
    test_match_instance.error_level = result
    test_match_instance.waiting_to_run = False
    test_match_instance.save()


def execute_python3_unit(solution, test):
    """Given specific argument as to how to run the test,
    move all of the files into the correct directories and
    execute the unit test. Note that care needs to be taken
    with regards to which operating system filepaths used.
    @solution - point to the solution to test
    @test - the test case to use"""
    script = 'python' if sys.platform == "win32" else 'python3'
    tmp_dir = os.path.join(settings.BASE_DIR, settings.MEDIA_TMP_TEST)
    init_dir = os.path.join(tmp_dir, '__init__.py')
    if sys.platform == "win32":
        tmp_dir = tmp_dir.replace('/', '\\')
        init_dir = init_dir.replace('/', '\\')
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    else:
        shutil.rmtree(tmp_dir)
        os.makedirs(tmp_dir)
    for submission in solution, test:
        for file in m.File.objects.filter(submission=submission):
            full_path = os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT, file.file.name)
            if sys.platform == "win32":
                full_path = full_path.replace('/', '\\')
            shutil.copy(full_path, tmp_dir)
    with open(init_dir, 'w+') as f:
        f.write('')
    args = " ".join([script, '-m', 'unittest', 'discover', '-p', '"*.py"'])
    proc = subprocess.Popen(args, cwd=tmp_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            shell=True)
    outb, errb = proc.communicate()
    outs = "" if outb is None else outb.decode('utf-8')
    errs = "" if errb is None else errb.decode('utf-8')
    output = outs + errs
    output = output.replace(tmp_dir, '[[testing_directory]]')
    return proc.returncode, output


def run_queued_tests(coursework):
    """go through all of the test data instances that are
    tagged as waiting to run for @coursework, and run them"""
    while True:
        tests = m.TestMatch.objects.filter(coursework=coursework, waiting_to_run=True)
        if tests.count() == 0:
            return
        for test in tests:
            run_test(test, execute_python3_unit)


def run_all_queued_on_thread(coursework):
    """Start a new thread to run queued tests on within @coursework"""
    threading.Thread(target=run_queued_tests, args=(coursework,)).start()


def run_test_on_thread(test_instance, exec_method):
    """Start a new thread and run the @test_instance,
    and use the specified @exec_method"""
    running = threading.Thread(target=run_test, args=(test_instance, exec_method))
    running.start()
