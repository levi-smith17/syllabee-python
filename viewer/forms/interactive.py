from django import forms


class ResetProgressConfirmationForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ResetProgressConfirmationForm, self).__init__(*args, **kwargs)