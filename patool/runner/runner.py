import os
import threading

from django.conf import settings
from django.db import transaction


import common.models as m
import test_match.matcher as matcher
import runner.pyunit
import runner.junit

TMP_DIR = os.path.join(settings.BASE_DIR, settings.MEDIA_TMP_TEST)


def get_correct_module(filename):
    if filename.split('.')[-1] == "py":
        return runner.pyunit
    if filename.split('.')[-1] in ["class", "jar", "java"]:
        return runner.junit
    raise Exception("unknown test type")


def run_test_in_thread(test_match):
    """Look at the specified @test_match, acquire the relevant files for
    the testing to happen, and then determine which execution / testing
    module should be used ot test it and execute appropriately"""
    solutions = test_match.solution.get_files()
    tests = test_match.solution.get_files()
    solution_dir = test_match.solution.path()
    test_dir = test_match.test.path()
    mod = get_correct_module(solutions[0])


def run_test_on_thread(test_instance):
    """Start a new thread and run the @test_instance,
    if it hasnt already been run"""
    running = threading.Thread(target=run_test_in_thread, args=(test_instance,))
    running.start()


def run_queued_tests(coursework):
    """go through all of the test data instances that are
    tagged as waiting to run for @coursework, and run them"""
    while True:
        tests = m.TestMatch.objects.filter(coursework=coursework, error_level=None)
        if tests.count() == 0:
            return
        for test in tests:
            run_test_on_thread(test)


def run_all_queued_on_thread(coursework):
    """Start a new thread to run queued tests on within @coursework"""
    threading.Thread(target=run_queued_tests, args=(coursework,)).start()


def run_signature_test(solution):
    """A new @solution submission has been created
    and we wish to run it against the appropriate
    signature test for that coursework"""
    tm = matcher.create_self_test(solution.id, "S", solution.coursework, solution.creator)
    run_test_on_thread(tm)


@transaction.atomic
def update_test_match(error_level, results, test_match):
    """update @test_match with the @results and
    the @error_level of running the tests"""
    result_submission = store_results(results, test_match)
    test_match.result = result_submission
    test_match.error_level = error_level
    test_match.save()


@transaction.atomic()
def store_results(content, tm):
    """Take in the @content from running a
    @tm test match instance, and save it,
    passing back a reference to submission"""
    result_sub = m.Submission(id=m.new_random_slug(m.Submission),
                              coursework=tm.coursework,
                              creator=tm.test.creator,
                              type=m.SubmissionType.TEST_RESULT,
                              student_name="Test Results",
                              peer_name="Test Results",
                              teacher_name="Results")
    result_sub.save()
    result_sub.save_content_file(content, "results.txt")
    return result_sub
