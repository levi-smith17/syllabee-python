from ..models import *
from django import forms


class QuickLinkForm(forms.ModelForm):
    restricted = forms.ChoiceField(initial=False, choices=BOOLEAN_CHOICES,
                                   help_text=QuickLink._meta.get_field('restricted').help_text)

    class Meta:
        model = QuickLink
        fields = '__all__'


class QuickLinkDeleteForm(forms.ModelForm):
    class Meta:
        model = QuickLink
        exclude = ('name', 'link', 'target',)