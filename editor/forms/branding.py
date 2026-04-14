from ..models import *
from django import forms


class BrandingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BrandingForm, self).__init__(*args, **kwargs)
        self.fields['background_image'].widget.attrs['disabled'] = False
        self.fields['core_values'].widget.attrs['style'] = 'height: 10rem;'

    class Meta:
        model = Branding
        fields = '__all__'
