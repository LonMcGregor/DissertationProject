from django.db import models as m
from django.contrib.auth.models import User


def upload_directory_path(cw, dev, type, filename):
    return 'uploads/%s/%s/%s/%s' % (cw, dev, type, filename)


def solution_directory_path(instance, filename):
    return upload_directory_path(instance.coursework, instance.developer, 'solution', filename)


def test_directory_path(instance, filename):
    return upload_directory_path(instance.coursework, instance.developer, 'test', filename)


def results_directory_path(instance, filename):
    return upload_directory_path(instance.coursework, instance.developer, 'testresult', filename)


def feedback_directory_path(instance, filename):
    return upload_directory_path(instance.coursework, instance.developer, 'feedback', filename)


class Course(m.Model):
    id = m.CharField(max_length=20, primary_key=True)
    name = m.CharField(max_length=128)


class EnrolledUser(m.Model):
    class Meta:
        unique_together = (('login', 'course'),)

    login = m.ForeignKey(User, m.CASCADE)
    course = m.ForeignKey(Course, m.CASCADE)


class Coursework(m.Model):
    name = m.CharField(max_length=128)
    descriptor = m.URLField()
    course = m.ForeignKey(Course, m.CASCADE)
    INVISIBLE = 'i'
    CLOSED = 'c'
    SOL_ONLY = 's'
    SOL_TEST = 'a'
    TEST_ONLY = 't'
    POSSIBLE_STATES = (
        (INVISIBLE, 'Invisible to Students'),
        (CLOSED, 'Closed for Submissions'),
        (SOL_ONLY, 'Accepting Solutions Only'),
        (SOL_TEST, 'Accepting Solutions and Tests'),
        (TEST_ONLY, 'Accepting Tests Only'),
    )
    state = m.CharField(max_length=1, choices=POSSIBLE_STATES, default=INVISIBLE)

    def is_visible(self):
        return self.state != self.INVISIBLE


class TestCase(m.Model):
    filepath = m.FileField(upload_to=test_directory_path, max_length=256)
    tester = m.ForeignKey(User, m.CASCADE)
    has_run = m.BooleanField()
    results = m.FileField(upload_to=results_directory_path, max_length=256, null=True)
    feedback = m.FileField(upload_to=feedback_directory_path, max_length=256, null=True)


class Solution(m.Model):
    class Meta:
        permissions = (
            ("view_solution", "Can view this solution"),
        )

    filepath = m.FileField(upload_to=solution_directory_path, max_length=256)
    coursework = m.ForeignKey(Coursework, m.CASCADE)
    developer = m.ForeignKey(User, m.CASCADE)
    test = m.ForeignKey(TestCase, m.SET_NULL, null=True)
