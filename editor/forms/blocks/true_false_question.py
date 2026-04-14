from core.widgets import QuillWidget
from django import forms
from editor.models import *


class TrueFalseQuestionForm(forms.ModelForm):
    text = forms.CharField(widget=None, help_text=TrueFalseQuestion._meta.get_field('text').help_text)

    def __init__(self, *args, **kwargs):
        super(TrueFalseQuestionForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget = QuillWidget(attrs={'disabled': False, 'required': True})
        self.fields['max_attempts'].required = False
        self.fields['max_points'].required = False

    class Meta:
        model = TrueFalseQuestion
        exclude = ('type', 'owner', 'response_block',)


class TrueFalseQuestionDeleteForm(forms.ModelForm):
    class Meta:
        model = TrueFalseQuestion
        fields = ()
