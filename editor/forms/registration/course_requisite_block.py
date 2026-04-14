from ...models import CourseRequisiteBlock
from django import forms

class CourseRequisiteBlockForm(forms.ModelForm):
    class Meta:
        model = CourseRequisiteBlock
        exclude = ('order', 'course',)


class CourseRequisiteBlockDeleteForm(forms.Form):
    class Meta:
        model = CourseRequisiteBlock
        exclude = '__all__'
