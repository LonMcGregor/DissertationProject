from django.db import models as m
from django.contrib.auth.models import User

# Create your models here.


def upload_directory_path(cw, dev, type, filename):
    return 'user_content/%s/%s/%s/%s' % (cw, dev, type, filename)


def solution_directory_path(instance, filename):
    return upload_directory_path(instance.coursework, instance.developer, 'solution', filename)


def test_directory_path(instance, filename):
    return upload_directory_path(instance.coursework, instance.developer, 'test', filename)


def results_directory_path(instance, filename):
    return upload_directory_path(instance.coursework, instance.developer, 'testresult', filename)


def feedback_directory_path(instance, filename):
    return upload_directory_path(instance.coursework, instance.developer, 'feedback', filename)


class Module(m.Model):
    id = m.CharField(max_length=20, primary_key=True)
    name = m.CharField(max_length=128)


class EnrolledUser(m.Model):
    class Meta:
        unique_together = (('login', 'module'),)

    login = m.ForeignKey(User, m.CASCADE)
    module = m.ForeignKey(Module, m.CASCADE)


class Coursework(m.Model):
    name = m.CharField(max_length=128)
    descriptor = m.URLField()
    module = m.ForeignKey(Module, m.CASCADE)


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


class MessageTemplate(m.Model):
    content = m.CharField(max_length=512)
    link = m.CharField(max_length=512)


class Message(m.Model):
    template = m.ForeignKey(MessageTemplate)
    rel = m.CharField(max_length=256)
    user = m.ForeignKey(User)
    hasBeenRead = m.BooleanField()
