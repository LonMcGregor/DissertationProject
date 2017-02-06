import django.forms as f
import student.models as m
import multiupload.fields as mff
from django.conf import settings


class CourseForm(f.Form):
    code = f.SlugField(label="Course Code", max_length=32)
    name = f.CharField(max_length=128, label="Course Name")
    student = f.CharField(widget=f.Textarea, label="Comma-Separated Enrolled Users")


class CourseworkForm(f.Form):
    name = f.CharField(label="Coursework Name", max_length=128)
    state = f.ChoiceField(label="Coursework State", choices=m.CourseworkState.POSSIBLE_STATES)
    # descriptor = mff.MultiFileField(min_num=1, max_num=settings.MAX_FILES_PER_SUBMISSION,
    #                                 max_file_size=settings.MAX_FILESIZE_FOR_UPLOADS,
    #                                 label="Files for Coursework descriptor")
    # oracle_exec = mff.MultiFileField(min_num=1, max_num=settings.MAX_FILES_PER_SUBMISSION,
    #                                  max_file_size=settings.MAX_FILESIZE_FOR_UPLOADS,
    #                                  label="Files for Oracle implementation")
    # identity = mff.MultiFileField(min_num=1, max_num=settings.MAX_FILES_PER_SUBMISSION,
    #                                 max_file_size=settings.MAX_FILESIZE_FOR_UPLOADS,
    #                                 label="Files for Identity test")
