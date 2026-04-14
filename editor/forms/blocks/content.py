from ..block import PrintableBlockForm
from core.widgets import QuillWidget
from django import forms
from editor.models import *


class ContentBlockCreateForm(PrintableBlockForm):
    def __init__(self, *args, **kwargs):
        super(ContentBlockCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = ContentBlock
        exclude = ('content', 'full_screen', 'type', 'owner', 'permalink', 'published',)


class ContentBlockUpdateForm(PrintableBlockForm):
    content = forms.CharField(widget=None, help_text=ContentBlock._meta.get_field('content').help_text)

    def __init__(self, *args, **kwargs):
        super(ContentBlockUpdateForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget = QuillWidget(attrs={'disabled': False, 'required': True})
        self.fields['image'].widget.attrs = {'disabled': False, 'required': False}

    class Meta:
        model = ContentBlock
        exclude = ('full_screen', 'type', 'owner', 'permalink', 'published',)
