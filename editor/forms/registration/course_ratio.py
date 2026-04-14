from ...models import CourseRatio
from django import forms


class CourseRatioForm(forms.ModelForm):
    class Meta:
        model = CourseRatio
        fields = '__all__'


class CourseRatioDeleteForm(forms.Form):
    class Meta:
        model = CourseRatio
        exclude = '__all__'
