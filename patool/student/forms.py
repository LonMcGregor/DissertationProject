import django.forms as f


class EasyMatchForm(f.Form):
    test = f.ChoiceField(label="One of your public test cases to run")
    solution = f.ChoiceField(label="One of your peer solutions to test")

    def __init__(self, my_tests, other_solutions, *args, **kwargs):
        super(EasyMatchForm, self).__init__(*args, **kwargs)
        self.fields['test'].choices = my_tests
        self.fields['solution'].choices = other_solutions
