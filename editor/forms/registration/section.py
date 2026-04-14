from ...models import *
from .course import clean_course_generic
from core.widgets import DatalistWidget
from django import forms
from django.core.exceptions import ValidationError


class SectionForm(forms.ModelForm):
    term = forms.CharField(widget=None, help_text=Section._meta.get_field('term').help_text)
    course = forms.CharField(widget=None, help_text=Section._meta.get_field('course').help_text)
    instructor = forms.CharField(widget=None, help_text=Section._meta.get_field('instructor').help_text)

    def __init__(self, *args, **kwargs):
        self.archived = kwargs.pop('archived') if 'archived' in kwargs else False
        self.user = kwargs.pop('user')
        super(SectionForm, self).__init__(*args, **kwargs)
        self.fields['term'].widget = DatalistWidget(model=Term, filters=(Q(archived=False)),
                                                    attrs={'disabled': False, 'required': True})
        self.fields['course'].widget = DatalistWidget(model=Course, filters=(Q(inactive=False)),
                                                      attrs={'disabled': False, 'required': True})
        self.fields['instructor'].widget = DatalistWidget(model=User, filters=(Q(groups__name='instructors')),
                                                          attrs={'disabled': False, 'required': True})
        if self.archived:
            self.fields['term'].disabled = True
            self.fields['course'].disabled = True
            self.fields['instructor'].disabled = True
            for field in self.fields.values():
                field.disabled = True

    class Meta:
        model = Section
        exclude = ('hash', 'owner',)

    def clean_course(self):
        return clean_course_generic(self)

    def clean_instructor(self):
        try:
            data = self.cleaned_data['instructor'].split(', ')
            data = User.objects.get(last_name=data[0], first_name=data[1], groups__name='instructors')
            return data
        except User.DoesNotExist:
            raise ValidationError('The provided instructor does not exist. Please select a valid instructor from '
                                  'the list.')
        except IndexError:
            raise ValidationError('The provided input is invalid. Please select a valid instructor from the list.')

    def clean_term(self):
        try:
            return Term.objects.get(term_code=self.cleaned_data['term'])
        except Term.DoesNotExist:
            raise ValidationError('The provided term does not exist. Please select a valid term from the list.')


class SectionAddForm(SectionForm):
    class Meta:
        model = Section
        exclude = ('archived_syllabus', 'hash', 'owner',)


class SectionDeleteForm(forms.Form):
    class Meta:
        model = Section
        exclude = '__all__'


class SectionFilterForm(forms.Form):
    course_prefixes_datalist = forms.CharField(widget=None, help_text='By Course Prefix', required=False)
    course_numbers_datalist = forms.CharField(widget=None, help_text='By Course Number', required=False)
    course_names_datalist = forms.CharField(widget=None, help_text='By Course Name', required=False)
    section_codes_datalist = forms.CharField(widget=None, help_text='By Section Code', required=False)
    terms_datalist = forms.CharField(widget=None, help_text='By Term', required=False)
    instructors_datalist = forms.CharField(widget=None, help_text='By Instructor', required=False)

    def __init__(self, *args, **kwargs):
        super(SectionFilterForm, self).__init__(*args, **kwargs)
        self.fields['course_prefixes_datalist'].widget = DatalistWidget(model=Course, filters=(Q(inactive=False)),
                                                                        values='prefix',
                                                                        attrs={'disabled': False, 'required': False})
        self.fields['course_numbers_datalist'].widget = DatalistWidget(model=Course, filters=(Q(inactive=False)),
                                                                       values='number',
                                                                       attrs={'disabled': False, 'required': False})
        self.fields['course_names_datalist'].widget = DatalistWidget(model=Course, filters=(Q(inactive=False)),
                                                                     values='name',
                                                                     attrs={'disabled': False, 'required': False})
        self.fields['section_codes_datalist'].widget = DatalistWidget(model=Section, values='section_code',
                                                                      attrs={'disabled': False, 'required': False})
        self.fields['terms_datalist'].widget = DatalistWidget(model=Term, values='term_code',
                                                              order_by='-term_code',
                                                              attrs={'disabled': False, 'required': False})
        self.fields['instructors_datalist'].widget = DatalistWidget(model=User, filters=(Q(groups__name='instructors')),
                                                                    attrs={'disabled': False, 'required': False})
