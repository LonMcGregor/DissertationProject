import django.forms as f


class EasyMatchForm(f.Form):
    test = f.ChoiceField(label="A test case to run")
    solution = f.ChoiceField(label="A solution to test")
    feedback_group = f.CharField(max_length=64, widget=f.HiddenInput, required=False)

    def __init__(self, my_tests, other_solutions, *args, **kwargs):
        super(EasyMatchForm, self).__init__(*args, **kwargs)
        self.fields['test'].choices = my_tests
        self.fields['solution'].choices = other_solutions
