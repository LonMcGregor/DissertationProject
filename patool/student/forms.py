import django.forms as f
import student.models as m
# import multiupload.fields as mff
from django.conf import settings


class FileUploadForm(f.Form):
    """A form that can be used to allow a student to upload a file,
    for example a solution or a test case for a coursework"""
    file_type = f.ChoiceField(label="File Type", choices=m.SubmissionType.POSSIBLE_TYPES)
    # chosen_files = mff.MultiFileField(min_num=1, max_num=settings.MAX_FILES_PER_SUBMISSION,
    #                                   max_file_size=settings.MAX_FILESIZE_FOR_UPLOADS,
    #                                   label="Selected files")
    keep_private = f.BooleanField(label="Keep this submission private?")


class TestMatchForm(f.Form):
    solution = f.SlugField(max_length=4, required=False,
                           label="Solution ID to be run (leave blank to use oracle)")
    test = f.SlugField(max_length=4, required=False,
                       label="Test ID to be run (leave blank to use identity test)# ")
