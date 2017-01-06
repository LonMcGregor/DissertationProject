import django.forms as f
import student.models as m


class CourseForm(f.Form):
    code = f.CharField(label="Course Code", max_length=32)
    name = f.CharField(max_length=128, label="Course Name")
    student = f.CharField(widget=f.Textarea, label="Comma-Separated Enrolled Users")


class CourseworkForm(f.Form):
    name = f.CharField(label="Coursework Name", max_length=128)
    descriptor = f.URLField(label="Coursework Descriptor URL")
    state = f.ChoiceField(label="Coursework State", choices=m.CourseworkState.POSSIBLE_STATES)
