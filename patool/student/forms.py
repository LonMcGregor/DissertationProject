import django.forms as f
import student.models as m


class FileUploadForm(f.Form):
    """A form that can be used to allow a student to upload a file,
    for example a solution or a test case for a coursework"""
    chosen_file = f.FileField(label="Selected File")
    file_type = f.HiddenInput()
