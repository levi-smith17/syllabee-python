from ..models import Portfolio, Section, User
from core.widgets import DatalistWidget
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q


class PortfolioForm(forms.ModelForm):
    section = forms.CharField(widget=None, help_text=Portfolio._meta.get_field('section').help_text)
    student = forms.CharField(widget=None, help_text=Portfolio._meta.get_field('student').help_text)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(PortfolioForm, self).__init__(*args, **kwargs)
        self.fields['section'].widget = DatalistWidget(model=Section, filters=Q(instructor=self.user,
                                                                                term__archived=False))
        self.fields['student'].widget = DatalistWidget(model=User)

    class Meta:
        model = Portfolio
        fields = '__all__'

    def clean_section(self):
        try:
            section_parts = self.cleaned_data['section'].split('-')
            return Section.objects.get(course__prefix=section_parts[0], course__number=section_parts[1],
                                       section_code=section_parts[2], term__term_code=section_parts[3])
        except Section.DoesNotExist:
            raise ValidationError('The provided section does not exist. Please select a valid section from the list.')


    def clean_student(self):
        try:
            name = self.cleaned_data['student'].split(', ')
            return User.objects.get(last_name=name[0], first_name=name[1])
        except User.DoesNotExist:
            raise ValidationError('The requested student does not exist.')


class PortfolioDeleteForm(forms.ModelForm):

    class Meta:
        model = Portfolio
        exclude = ('section', 'student', 'completed_reviews',)
