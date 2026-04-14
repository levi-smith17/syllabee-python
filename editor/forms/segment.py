from ..models import *
from core.forms import BOOLEAN_CHOICES
from django import forms


class SegmentForm(forms.ModelForm):
    printing_optional = forms.ChoiceField(initial=False, choices=BOOLEAN_CHOICES,
                                          help_text=Segment._meta.get_field('printing_optional').help_text)

    def __init__(self, *args, **kwargs):
        super(SegmentForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs['style'] = 'height: 10rem;'

    class Meta:
        model = Segment
        exclude = ('owner',)


class SegmentDeleteForm(forms.ModelForm):
    class Meta:
        model = Segment
        exclude = ('name', 'description', 'print_heading', 'printing_optional', 'owner',)
