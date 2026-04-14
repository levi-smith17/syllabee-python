from ...models import *
from django import forms
from django.forms.widgets import NumberInput


class TermForm(forms.ModelForm):
    start_date = forms.DateField(widget=NumberInput(attrs={'type': 'date'}),
                                 help_text=Term._meta.get_field('start_date').help_text)
    end_date = forms.DateField(widget=NumberInput(attrs={'type': 'date'}),
                               help_text=Term._meta.get_field('end_date').help_text)
    has_midpoint_break = forms.ChoiceField(initial=False, choices=BOOLEAN_CHOICES,
                                           help_text=Term._meta.get_field('has_midpoint_break').help_text)
    supports_master_syllabi = forms.ChoiceField(initial=False, choices=BOOLEAN_CHOICES,
                                                help_text=Term._meta.get_field('supports_master_syllabi').help_text)

    def __init__(self, *args, **kwargs):
        self.archived = kwargs.pop('archived') if 'archived' in kwargs else False
        super(TermForm, self).__init__(*args, **kwargs)
        if self.archived:
            self.fields['term_code'].disabled = True
            for field in self.fields.values():
                field.disabled = True

    class Meta:
        model = Term
        exclude = ('archived',)


class TermArchiveDeleteForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = ()
