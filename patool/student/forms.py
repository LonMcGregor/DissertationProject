import django.forms as f


class TestMatchForm(f.Form):
    solution = f.SlugField(max_length=4, required=False,
                           label="Solution ID to be run (leave blank to use oracle)")
    test = f.SlugField(max_length=4, required=False,
                       label="Test ID to be run (leave blank to use identity test)# ")
