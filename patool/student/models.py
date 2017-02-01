import random
from django.db import models as m
from django.contrib.auth.models import User
import string


def upload_directory_path(instance, filename):
    """For a given @instance of File, and a client-side @filename,
    generate a path where the file should be stored on the system
    This will be appended to the settings BASE_DIR and MEDIA_ROOT"""
    return '%s/%s/%s/%s/originals/%s' % (instance.submission.coursework.id,
                                         instance.submission.creator.id,
                                         instance.submission.type.id,
                                         instance.submission.id,
                                         filename)


slug_characters = ['-', '_'] + list(string.ascii_letters) + list(string.digits)


def new_random_slug(model, primary_key='id', length=4):
    """For a given @model, find a new random slug of @length
    which is unique against the primary key of the model"""
    exists = True
    new_slug = ""
    while exists:
        for count in range(length):
            new_slug += random.choice(slug_characters)
        exists = model.objects.filter(**{primary_key: new_slug}).count() > 0
    return new_slug


class Course(m.Model):
    name = m.CharField(max_length=128)
    code = m.SlugField(max_length=32, primary_key=True)


class EnrolledUser(m.Model):
    class Meta:
        unique_together = (('login', 'course'),)

    login = m.ForeignKey(User, m.CASCADE)
    course = m.ForeignKey(Course, m.CASCADE)


class CourseworkState:
    INVISIBLE = 'i'
    CLOSED = 'c'
    UPLOAD = 'u'
    FEEDBACK = 'f'
    POSSIBLE_STATES = (
        (INVISIBLE, 'Invisible to Students'),
        (CLOSED, 'Closed for Submissions'),
        (UPLOAD, 'Accepting Uploads'),
        (FEEDBACK, 'Accepting Feedback'),
    )


class Coursework(m.Model):
    id = m.SlugField(max_length=4, primary_key=True)
    name = m.CharField(max_length=128)
    course = m.ForeignKey(Course, m.CASCADE)
    state = m.CharField(max_length=1,
                        choices=CourseworkState.POSSIBLE_STATES,
                        default=CourseworkState.INVISIBLE)
    file_pipe = m.CharField(max_length=128)
    test_pipe = m.CharField(max_length=128)

    def is_visible(self):
        return self.state != CourseworkState.INVISIBLE


class SubmissionType:
    SOLUTION = 's'
    TEST_CASE = 'c'
    TEST_RESULT = 'r'
    FEEDBACK = 'f'
    CW_DESCRIPTOR = 'd'
    ORACLE_EXECUTABLE = 'e'
    IDENTITY_TEST = 'i'
    POSSIBLE_TYPES = (
        (SOLUTION, 'Solution to Coursework'),
        (TEST_CASE, 'Test Case for Solution'),
        (TEST_RESULT, 'Results of Running Test Case'),
        (FEEDBACK, 'Feedback for a Solution'),
        (CW_DESCRIPTOR, 'Coursework Task Descriptor'),
        (ORACLE_EXECUTABLE, 'Executable that will act as Oracle'),
        (IDENTITY_TEST, 'Test to ensure Solution matches Interface'),
    )


class Submission(m.Model):
    id = m.SlugField(max_length=4, primary_key=True)
    coursework = m.ForeignKey(Coursework, m.CASCADE)
    creator = m.ForeignKey(User, m.CASCADE)
    type = m.CharField(max_length=1, choices=SubmissionType.POSSIBLE_TYPES)
    private = m.BooleanField()


class File(m.Model):
    file = m.FileField(upload_to=upload_directory_path)
    submission = m.ForeignKey(Submission, m.CASCADE, null=True)


class TestMatch(m.Model):
    id = m.SlugField(max_length=4, primary_key=True)
    test = m.ForeignKey(Submission, m.CASCADE, related_name="tm_test_sub")
    solution = m.ForeignKey(Submission, m.CASCADE, related_name="tm_sol_sub")
    result = m.ForeignKey(Submission, m.CASCADE, null=True, related_name="tm_res_sub")
    feedback = m.ForeignKey(Submission, m.CASCADE, null=True, related_name="tm_fdbk_sub")
    teacher_feedback = m.ForeignKey(Submission, m.CASCADE, null=True, related_name="tm_tfdbk_sub")
    error_level = m.IntegerField(null=True)
    coursework = m.ForeignKey(Coursework, m.CASCADE, related_name="tm_cw")
    initiator = m.ForeignKey(User, m.CASCADE, related_name="tm_init")
    marker = m.ForeignKey(User, m.CASCADE, null=True, related_name="tm_marker")
    waiting_to_run = m.BooleanField()
    visible_to_developer = m.BooleanField()
