import django.forms as f
import student.models as m


class FileUploadForm(f.Form):
    chosen_file = f.FileField(label="Selected File")
    file_type = f.ChoiceField(label="File Type", choices=m.FileType.POSSIBLE_TYPES)
