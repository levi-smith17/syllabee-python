from django import forms
from core.widgets import QuillWidget
from editor.models import *


class MultipleChoiceQuestionForm(forms.ModelForm):
    text = forms.CharField(widget=None, help_text=MultipleChoiceQuestion._meta.get_field('text').help_text)

    def __init__(self, *args, **kwargs):
        super(MultipleChoiceQuestionForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget = QuillWidget(attrs={'disabled': False, 'required': True})
        self.fields['max_attempts'].required = False
        self.fields['max_points'].required = False

    class Meta:
        model = MultipleChoiceQuestion
        exclude = ('type', 'owner', 'response_block',)


class MultipleChoiceQuestionDeleteForm(forms.ModelForm):
    class Meta:
        model = MultipleChoiceQuestion
        fields = ()


class MultipleChoiceQuestionResponseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MultipleChoiceQuestionResponseForm, self).__init__(*args, **kwargs)
        self.fields['response'].widget.attrs['rows'] = 2

    class Meta:
        model = MultipleChoiceQuestionResponse
        exclude = ('owner', 'multiple_choice_question',)


ResponseFormSet = forms.inlineformset_factory(MultipleChoiceQuestion, MultipleChoiceQuestionResponse,
                                              can_delete=False, form=MultipleChoiceQuestionResponseForm,
                                              fields=('identifier', 'response',), extra=0, min_num=4, max_num=4,
                                              validate_min=True)
