import random
import string

from django.contrib.auth.models import User
from django.db import models as m


def upload_directory_path(instance, filename):
    """For a given @instance of File, and a client-side @filename,
    generate a path where the file should be stored on the system
    This will be appended to the settings BASE_DIR and MEDIA_ROOT"""
    return '%s/%s/%s/originals/%s' % (instance.submission.coursework.id,
                                      instance.submission.creator.id,
                                      instance.submission.id,
                                      filename)


slug_characters = ['-', '_'] + list(string.ascii_letters) + list(string.digits)


def new_random_slug(model, primary_key='id', length=8):
    """For a given @model, find a new random slug of @length
    which is unique against the primary key of the model. can
    specify a @primary_key if it is different to 'id'"""
    exists = True
    new_slug = ""
    while exists:
        new_slug = ""
        for count in range(length):
            new_slug += random.choice(slug_characters)
        exists = model.objects.filter(**{primary_key: new_slug}).count() > 0
    return new_slug


# noinspection PyClassHasNoInit
class Course(m.Model):
    name = m.CharField(max_length=128)
    code = m.SlugField(max_length=32, primary_key=True)


# noinspection PyClassHasNoInit
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
        (UPLOAD, 'Self-Testing and Solutions'),
        (FEEDBACK, 'Peer-Testing and Feedback'),
    )


# noinspection PyClassHasNoInit
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
        """Show if the coursework state allows it to be visible"""
        return self.state != CourseworkState.INVISIBLE


class SubmissionType:
    SOLUTION = 's'
    TEST_CASE = 'c'
    TEST_RESULT = 'r'
    FEEDBACK = 'f'
    CW_DESCRIPTOR = 'd'
    ORACLE_EXECUTABLE = 'e'
    SIGNATURE_TEST = 'i'
    POSSIBLE_TYPES = (
        (SOLUTION, 'Solution to Coursework'),
        (TEST_CASE, 'Test Case for Solution'),
        (TEST_RESULT, 'Results of Running Test Case'),
        (FEEDBACK, 'Feedback for a Solution'),
        (CW_DESCRIPTOR, 'Coursework Task Descriptor, sample files'),
        (ORACLE_EXECUTABLE, 'Executable that tests run against that gives expected output'),
        (SIGNATURE_TEST, 'Test solution matches signature, interface, compiles, etc.'),
    )


# noinspection PyClassHasNoInit
class Submission(m.Model):
    id = m.SlugField(max_length=4, primary_key=True)
    coursework = m.ForeignKey(Coursework, m.CASCADE)
    creator = m.ForeignKey(User, m.CASCADE)
    type = m.CharField(max_length=1, choices=SubmissionType.POSSIBLE_TYPES)
    student_name = m.CharField(max_length=64, null=True)
    peer_name = m.CharField(max_length=64, null=True)
    teacher_name = m.CharField(max_length=64, null=True)


# noinspection PyClassHasNoInit
class File(m.Model):
    file = m.FileField(upload_to=upload_directory_path)
    submission = m.ForeignKey(Submission, m.CASCADE, null=True)


class TestType:
    SELF = 's'
    PEER = 'p'
    TEACHER = 't'
    POSSIBLE_TYPES = (
        (SELF, 'A Self-Test, the developer of the solution testing their own code'),
        (PEER, 'A Peer-Test, the tester is testing someone else\'s code'),
        (TEACHER, 'A teacher wants to test the code of a student')
    )


# noinspection PyClassHasNoInit
class TestMatch(m.Model):
    id = m.SlugField(max_length=4, primary_key=True)
    test = m.ForeignKey(Submission, m.CASCADE, related_name="tm_test_sub")
    solution = m.ForeignKey(Submission, m.CASCADE, related_name="tm_sol_sub")
    result = m.ForeignKey(Submission, m.CASCADE, null=True, related_name="tm_res_sub")
    error_level = m.IntegerField(null=True)
    coursework = m.ForeignKey(Coursework, m.CASCADE, related_name="tm_cw")
    type = m.CharField(max_length=1, choices=SubmissionType.POSSIBLE_TYPES)
