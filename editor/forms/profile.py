from ..models import *
from django import forms


class ProfileForm(forms.ModelForm):
    institution_id = forms.CharField(disabled=True)
    first_name = forms.CharField(disabled=True)
    last_name = forms.CharField(disabled=True)

    field_order = ['institution_id', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].initial = self.user.first_name
        self.fields['last_name'].initial = self.user.last_name
        self.fields['picture'].widget.attrs['disabled'] = False

    class Meta:
        model = Profile
        exclude = ('user',)