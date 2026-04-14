from ...models import *
from django import forms


class TermLengthForm(forms.ModelForm):
    class Meta:
        model = TermLength
        fields = '__all__'


class TermLengthDeleteForm(forms.ModelForm):
    class Meta:
        model = TermLength
        exclude = ('name', 'num_weeks', 'can_have_midpoint_break',)
