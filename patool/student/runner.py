from django.conf import settings
import student.models as m
import sys
import subprocess
from django.core.files.base import ContentFile
from django.db import transaction
import shutil
import os


@transaction.atomic
def run_test(test_data_instance):
    script = 'python' if sys.platform == "win32" else 'python3'
    solution_file = os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT,
                                 str(test_data_instance.solution.filepath))
    test_path = os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT,
                             str(test_data_instance.test.filepath))
    test_file = test_path.split('/')[::-1][0]
    if sys.platform == "win32":
        solution_file = solution_file.replace("/", "\\")
        test_path = test_path.replace('/', '\\')
    result, output = execute(script, solution_file, test_path, test_file)
    result_file = m.File(coursework=test_data_instance.coursework,
                         creator=test_data_instance.test.creator, type=m.FileType.TEST_RESULT)
    result_file.filepath.save('results.txt', ContentFile(output))
    # todo who is creator? if in current cw, then it is test writer. if invoked later... is teacher?
    result_file.save()
    test_data_instance.results = result_file
    test_data_instance.error_level = result
    test_data_instance.waiting_to_run = False
    test_data_instance.save()


def execute(script, solution_file, test_dir, test_file):
    # todo FOR NOW ONLY SUPPORT RUNNING THIS ONCE AT A TIME
    media_dir = os.path.join(settings.BASE_DIR, settings.MEDIA_TMP_TEST)
    init_dir = os.path.join(media_dir, '__init__.py')
    if sys.platform == "win32":
        media_dir = media_dir.replace('/', '\\')
        init_dir = init_dir.replace('/', '\\')
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)
    else:
        shutil.rmtree(media_dir)
        os.makedirs(media_dir)
    shutil.copy(solution_file, media_dir)
    shutil.copy(test_dir, media_dir)
    with open(init_dir, 'w+') as f:
        f.write('')
    args = " ".join([script, '-m', 'unittest', '-v', test_file])
    proc = subprocess.Popen(args, cwd=media_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            shell=True)
    outb, errb = proc.communicate()
    outs = "" if outb is None else outb.decode('utf-8')
    errs = "" if errb is None else errb.decode('utf-8')
    output = outs + errs
    return proc.returncode, output


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
        details = {'solution': item, 'test': matching_item, 'initiator': matching_item.creator}
    elif item_type == m.FileType.TEST_CASE:
        details = {'solution': matching_item, 'test': item, 'initiator': item.creator}
    else:
        raise Exception("invalid type")
    tr = m.TestData(coursework=coursework, **details)
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
