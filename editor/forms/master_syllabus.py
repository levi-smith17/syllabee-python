from ..models import *
from core.widgets import QuillWidget
from django import forms


class MasterSyllabusCreateForm(forms.ModelForm):
    interactive_view = forms.ChoiceField(initial=True, choices=((True, 'Interactive'), (False, 'Traditional')),
                                         help_text=MasterSyllabus._meta.get_field('interactive_view').help_text)
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(MasterSyllabusCreateForm, self).__init__(*args, **kwargs)
        self.fields['interactive_view'].label = 'Student view'
        self.fields['office_hours'].widget.attrs['style'] = 'height: 10rem;'
        self.fields['term'].queryset = (Term.objects
                                        .filter(archived=False, supports_master_syllabi=True)
                                        .exclude(mastersyllabus__owner=self.user))

    class Meta:
        model = MasterSyllabus
        exclude = ('owner', 'locked', 'max_attempts', 'max_points', 'points_ladder', 'points_ladder_deduction',
                   'prohibit_backtracking', 'randomize_responses', 'timeout',)


class MasterSyllabusDeleteForm(forms.ModelForm):
    class Meta:
        model = MasterSyllabus
        fields = ()


class MasterSyllabusInteractiveForm(forms.ModelForm):
    points_ladder = forms.ChoiceField(initial=False, choices=BOOLEAN_CHOICES,
                                      help_text=MasterSyllabus._meta.get_field('points_ladder').help_text)
    prohibit_backtracking = forms.ChoiceField(initial=False, choices=BOOLEAN_CHOICES,
                                              help_text=(MasterSyllabus._meta
                                                         .get_field('prohibit_backtracking').help_text))
    randomize_responses = forms.ChoiceField(initial=True, choices=BOOLEAN_CHOICES,
                                            help_text=MasterSyllabus._meta.get_field('randomize_responses').help_text)

    class Meta:
        model = MasterSyllabus
        exclude = ('owner', 'locked', 'office_hours', 'term', 'interactive_view',)


class MasterSyllabusLockForm(forms.ModelForm):
    class Meta:
        model = MasterSyllabus
        fields = ()


class MasterSyllabusUpdateForm(forms.ModelForm):
    interactive_view = forms.ChoiceField(initial=True, choices=((True, 'Interactive'), (False, 'Traditional')),
                                         help_text=MasterSyllabus._meta.get_field('interactive_view').help_text)
    def __init__(self, *args, **kwargs):
        super(MasterSyllabusUpdateForm, self).__init__(*args, **kwargs)
        self.fields['interactive_view'].label = 'Student view'
        self.fields['office_hours'].widget.attrs['style'] = 'height: 10rem;'

    class Meta:
        model = MasterSyllabus
        exclude = ('owner', 'locked', 'term', 'max_attempts', 'max_points', 'points_ladder', 'points_ladder_deduction',
                   'prohibit_backtracking', 'randomize_responses', 'timeout')
