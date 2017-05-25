import os
import re
import shutil
import subprocess


def prepare_temp_directory(path):
    """Create or clean up a temporary
    working directory at @path"""
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        shutil.rmtree(path)
        os.makedirs(path)
    init_dir = os.path.join(path, '__init__.py')
    with open(init_dir, 'w+') as f:
        f.write('')


def copy_all(files, path, tmp_dir):
    """for list of @files at path,
    copy them to @tmp_dir"""
    for file in files:
        full_path = os.path.join(path, file)
        shutil.copy(full_path, tmp_dir)


def process_results(content):
    """Process @content of results of running test
    to clean up any unwanted information"""
    content2 = re.sub(r"(File [\"\']).+/(python[0-9.]+)/(.+[\"\'])", r"\1/\2/\3", content)
    return re.sub(r"(File [\"\']).+/var/tmp/(.+[\"\'])", r"\1/\2", content2)


def execute_test(tmp_dir, path_solutions, solutions, path_tests, tests):
    """Given specific argument as to how to run the test,
    move all of the files into the correct directories and
    execute the test. 
    @tmp_dir - a tmp dir to run test in
    @path_solutions - path to where solution files located
    @solutions - list of solution files to copy to tmp dir
    @path_tests - path to where testing files located
    @tests - list of test files to copy to tmp dir"""
    prepare_temp_directory(tmp_dir)
    path_solutions = os.path.join(path_solutions)
    # todo dunno what im doing here
    copy_all(solutions, path_solutions, tmp_dir)
    copy_all(tests, path_tests, tmp_dir)
    args = 'python -m unittest discover -p "*.py"'
    proc = subprocess.Popen(args, cwd=tmp_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            shell=True)
    outb, errb = proc.communicate()
    outs = "" if outb is None else outb.decode('utf-8')
    errs = "" if errb is None else errb.decode('utf-8')
    output = outs + errs
    cleaned_output = process_results(output)
    return proc.returncode, cleaned_output


def solution_uploaded(solution):
    """a @solution is uploaded. python does
    not require compilation so do nothing"""
    pass
