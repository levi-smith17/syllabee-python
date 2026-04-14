from django import forms


class PrintConfirmationForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(PrintConfirmationForm, self).__init__(*args, **kwargs)
