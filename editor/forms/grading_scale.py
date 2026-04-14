from ..models import *
from django import forms


class GradingScaleGradeForm(forms.ModelForm):
    class Meta:
        model = GradingScaleGrade
        exclude = ('grading_scale',)


GradeFormSet = forms.inlineformset_factory(GradingScale, GradingScaleGrade, can_delete=True, form=GradingScaleGradeForm,
                                           fields=('letter', 'percent_start', 'percent_end',), extra=0, min_num=1,
                                           max_num=15, validate_min=True)


class GradingScaleForm(forms.ModelForm):
    class Meta:
        model = GradingScale
        exclude = ('owner',)


class GradingScaleDeleteForm(forms.ModelForm):
    class Meta:
        model = GradingScale
        exclude = ('owner', 'name',)






