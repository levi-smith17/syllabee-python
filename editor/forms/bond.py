from ..models import *
from django import forms


class BondForm(forms.ModelForm):
    class Meta:
        model = Bond
        exclude = ('owner', 'segment', 'order',)


class BondDeleteForm(forms.ModelForm):
    class Meta:
        model = Bond
        exclude = ('owner', 'segment', 'block', 'order',)
