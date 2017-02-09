import django.forms as f

import student.models as m


class CourseForm(f.Form):
    code = f.SlugField(label="Course Code", max_length=32)
    name = f.CharField(max_length=128, label="Course Name")
    student = f.CharField(widget=f.Textarea, label="Comma-Separated Enrolled Users")


class CourseworkForm(f.Form):
    name = f.CharField(label="Coursework Name", max_length=128)
    state = f.ChoiceField(label="Coursework State", choices=m.CourseworkState.POSSIBLE_STATES)


class TestMatchForm(f.Form):
    solution_sub = f.SlugField(label="Run Solution", max_length=4)
    test_sub = f.SlugField(label="against Test Case", max_length=4)
    to_be_marked_by = f.CharField(label="to be Marked by", max_length=64)
    visible_to_developer = f.BooleanField(label="Visible to developer", required=False)
    coursework = f.SlugField(widget=f.HiddenInput, max_length=4)
