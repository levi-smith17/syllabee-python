from ..block import PrintableBlockForm
from django import forms
from editor.models import *


class DetailsBlockForm(PrintableBlockForm):
    class Meta:
        model = DetailsBlock
        exclude = ('full_screen', 'type', 'owner', 'published', 'permalink',)


class DetailsBlockDetailForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DetailsBlockDetailForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs['style'] = 'height: 10rem;'

    class Meta:
        model = DetailsBlockDetail
        exclude = ('owner', 'details_block', 'order',)


class DetailsBlockDetailDeleteForm(forms.ModelForm):
    class Meta:
        model = DetailsBlockDetail
        exclude = ('owner', 'details_block', 'summary', 'content', 'order',)
