import django.forms as f

import student.models as m
from runner import matcher


class CourseForm(f.Form):
    code = f.SlugField(label="Course Code", max_length=32)
    name = f.CharField(max_length=128, label="Course Name")
    student = f.CharField(widget=f.Textarea, label="Comma-Separated Enrolled Users")


class CourseworkForm(f.Form):
    name = f.CharField(label="Coursework Name", max_length=128)
    state = f.ChoiceField(label="Coursework State", choices=m.CourseworkState.POSSIBLE_STATES)


class AutoTestMatchForm(f.Form):
    algorithm = f.ChoiceField(label="Choice of Match Algorithm", choices=matcher.AVAILABLE_MATCHES)
    assign_markers = f.BooleanField(label="Assign Markers", required=False)
    visible_to_developer = f.BooleanField(label="Visible to developer", required=False)

