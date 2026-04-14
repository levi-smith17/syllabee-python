from django import forms

from editor.models import MasterBondSection

BOOLEAN_CHOICES = (
    (True, 'Yes'),
    (False, 'No'),
)


class ArrangeForm(forms.Form):
    ordering = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'ordering-submit'}))


class LtiDeepLinkForm(forms.Form):
    section = forms.ModelChoiceField(label="Section", queryset=None)
    lti_launch_id = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.lti_launch_identifier = kwargs.pop('lti_launch_id')
        super(LtiDeepLinkForm, self).__init__(*args, **kwargs)
        self.fields['lti_launch_id'].initial = self.lti_launch_identifier
        self.fields['section'].queryset = MasterBondSection.objects.filter(section__term__archived=False)
