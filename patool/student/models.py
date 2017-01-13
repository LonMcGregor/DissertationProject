from django.db import models as m
from django.contrib.auth.models import User


def upload_directory_path(instance, filename):
    return '%s/%s/%s/%s' % (instance.coursework.id, instance.creator, instance.type, filename)


class Course(m.Model):
    name = m.CharField(max_length=128)
    code = m.SlugField(max_length=32, unique=True)


class EnrolledUser(m.Model):
    class Meta:
        unique_together = (('login', 'course'),)

    login = m.ForeignKey(User, m.CASCADE)
    course = m.ForeignKey(Course, m.CASCADE)


class CourseworkState:
    INVISIBLE = 'i'
    CLOSED = 'c'
    SOLUTIONS_ONLY = 's'
    SOLUTIONS_TEST = 'b'
    TEST_ONLY = 't'
    POSSIBLE_STATES = (
        (INVISIBLE, 'Invisible to Students'),
        (CLOSED, 'Closed for Submissions'),
        (SOLUTIONS_ONLY, 'Accepting Solutions Only'),
        (SOLUTIONS_TEST, 'Accepting Solutions and Tests'),
        (TEST_ONLY, 'Accepting Tests Only'),
    )


class Coursework(m.Model):
    name = m.CharField(max_length=128)
    descriptor = m.URLField()
    course = m.ForeignKey(Course, m.CASCADE)
    state = m.CharField(max_length=1,
                        choices=CourseworkState.POSSIBLE_STATES,
                        default=CourseworkState.INVISIBLE)

    def is_visible(self):
        return self.state != CourseworkState.INVISIBLE


class FileType:
    SOLUTION = 's'
    TEST_CASE = 'c'
    TEST_RESULT = 'r'
    FEEDBACK = 'f'
    POSSIBLE_TYPES = (
        (SOLUTION, 'Solution to Coursework'),
        (TEST_CASE, 'Test Case for Solution'),
        (TEST_RESULT, 'Results of Running Test Case'),
        (FEEDBACK, 'Feedback for a Solution'),
    )


class File(m.Model):
    filepath = m.FileField(upload_to=upload_directory_path)
    coursework = m.ForeignKey(Coursework, m.CASCADE)
    creator = m.ForeignKey(User, m.CASCADE)
    type = m.CharField(max_length=1, choices=FileType.POSSIBLE_TYPES)


class TestData(m.Model):
    class Meta:
        unique_together = (('test', 'solution', 'coursework', 'initiator'),)

    test = m.ForeignKey(File, m.CASCADE, related_name="test_data_test_file_relation")
    solution = m.ForeignKey(File, m.CASCADE, related_name="test_data_solution_file_relation")
    results = m.ForeignKey(File, m.CASCADE, null=True,
                           related_name="test_data_results_file_relation")
    feedback = m.ForeignKey(File, m.CASCADE, null=True,
                            related_name="test_data_feedback_file_relation")
    error_level = m.IntegerField(null=True)
    coursework = m.ForeignKey(Coursework, m.CASCADE, related_name='test_data_coursework_relation')
    initiator = m.ForeignKey(User, m.CASCADE, related_name='test_data_inititating_user_relation')
    waiting_to_run = m.BooleanField(default=True)
