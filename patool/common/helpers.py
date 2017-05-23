
import common.models as m


def test_match_for_results(submission):
    """Given that a results @submission only is ever attached to
    a single test match, we can return it"""
    return m.TestMatch.objects.get(result=submission)


def get_files(submission):
    """For a given @submission instance, get the
    names of the files back as a list"""
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


def get_test_match(tm_id):
    """Given an @tm_id, get the associated test match"""
    return m.TestMatch.objects.filter(id=tm_id).first()
