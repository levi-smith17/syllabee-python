from ..models import *
from django import forms
from django.core.exceptions import ValidationError



VISIBILITY_CHOICES = (
    (True, 'Visible to Students'),
    (False, 'Hidden from Students'),
)


class MasterBondForm(forms.ModelForm):
    class Meta:
        model = MasterBond
        exclude = ('owner', 'master_syllabus', 'order',)


class MasterBondDeleteForm(forms.ModelForm):
    class Meta:
        model = MasterBond
        exclude = ('owner', 'master_syllabus', 'segment', 'section', 'order',)


class MasterBondSectionForm(forms.ModelForm):
    section = forms.ModelChoiceField(queryset=Section.objects.all())

    def __init__(self, *args, **kwargs):
        self.term_id = kwargs.pop('term_id')
        self.user = kwargs.pop('user')
        super(MasterBondSectionForm, self).__init__(*args, **kwargs)
        term = Term.objects.get(pk=self.term_id)
        self.fields['section'].queryset = (Section.objects
                                           .filter(instructor=self.user,
                                                   term__start_date__gte=term.start_date,
                                                   term__end_date__lte=term.end_date))

    class Meta:
        model = MasterBondSection
        exclude = ('master_bond', 'owner',)

    def clean_section(self):
        try:
            return Section.objects.get(pk=self.cleaned_data['section'].id)
        except Section.DoesNotExist:
            raise ValidationError('The provided section does not exist. Please select a valid section from the list.')


class MasterBondSegmentForm(forms.ModelForm):
    class Meta:
        model = Segment
        exclude = ('name', 'description', 'print_heading', 'printing_optional', 'owner',)


class MasterBondSegmentsForm(forms.Form):
    segments = forms.modelformset_factory(Segment, can_delete=False, form=MasterBondSegmentForm,
                                          fields=(), extra=0, min_num=1, max_num=100)


class MasterBondSectionsForm(forms.Form):
    sections = forms.modelformset_factory(MasterBondSection, can_delete=True, form=MasterBondSectionForm,
                                          fields=('section',), extra=0, min_num=1, max_num=10)


class MasterBondUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.master_syllabus_id = kwargs.pop('master_syllabus_id')
        self.user = kwargs.pop('user')
        super(MasterBondUpdateForm, self).__init__(*args, **kwargs)
        self.fields['section'].queryset = (Section.objects
                                           .filter(instructor=self.user,
                                                   term__start_date__exact=(MasterSyllabus.objects
                                                                            .get(pk=self.master_syllabus_id))
                                                   .term.start_date))

    class Meta:
        model = MasterBond
        exclude = ('owner', 'master_syllabus', 'segment', 'order',)


class MasterBondVisibilityForm(forms.ModelForm):
    visibility = forms.ChoiceField(initial=False, choices=VISIBILITY_CHOICES,
                                   help_text=MasterBond._meta.get_field('visibility').help_text)

    class Meta:
        model = MasterBond
        fields = ('visibility',)
