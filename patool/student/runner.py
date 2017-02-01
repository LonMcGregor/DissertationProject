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
    """Go through the @test_data_instance and run the
    test case against the solution. Store the data setting
    the results to be created by the initiator (which will
     likely be the test creator). Then update the database"""
    if not test_data_instance.waiting_to_run:
        return
    script = 'python' if sys.platform == "win32" else 'python3'
    solution_file = os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT,
                                 str(test_data_instance.solution.file))
    test_path = os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT,
                             str(test_data_instance.test.file))
    test_file = test_path.split('/')[::-1][0]
    if sys.platform == "win32":
        solution_file = solution_file.replace("/", "\\")
        test_path = test_path.replace('/', '\\')
    result, output = execute(script, solution_file, test_path, test_file)
    result_file = m.File(coursework=test_data_instance.coursework,
                         creator=test_data_instance.initiator, type=m.SubmissionType.TEST_RESULT)
    result_file.file.save('results.txt', ContentFile(output))
    result_file.save()
    test_data_instance.results = result_file
    test_data_instance.error_level = result
    test_data_instance.waiting_to_run = False
    test_data_instance.save()


def execute(script, solution_file, test_dir, test_file):
    """Given specific argument as to how to run the test,
    move all of the files into the correct directories and
    execute the unit test. Note that care needs to be taken
    with regards to which operating system filepaths used.
    @script - which python executable to use
    @solution_file - point to the solution file to test
    @test_dir - the directory holding the test case
    @test_file - the name of the file containing the test"""
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
    if file_type not in [m.FileType.SOLUTION, m.FileType.TEST_CASE]:
        raise Exception("bas file type")
    items = m.File.objects.filter(coursework=coursework, type=file_type).exclude(creator=user)
    for item in items:
        kwargs = {"coursework": coursework}
        if file_type == m.FileType.SOLUTION:
            kwargs["solution"] = item
        else:
            kwargs["test"] = item
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
        return
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


def run_queued_tests():
    """go through all of the test data instances that are
    tagged as waiting to run, and run them"""
    while True:
        tests = m.TestData.objects.filter(waiting_to_run=True)
        if tests.count() == 0:
            return
        for test in tests:
            run_test(test)
