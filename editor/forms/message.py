from ..models import *
from django import forms


class MessageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['body'].widget.attrs['style'] = 'height: 17rem;'

    class Meta:
        model = Message
        exclude = ('owner',)


class MessageDeleteForm(forms.ModelForm):

    class Meta:
        model = Message
        exclude = ('name', 'description', 'subject', 'body', 'owner',)
