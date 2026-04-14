from ..models import *
from core.widgets import DatalistWidget
from django import forms


class MasterBondSectionFilterForm(forms.Form):
    course_prefixes_datalist = forms.CharField(widget=None, help_text='By Course Prefix', required=False)
    course_numbers_datalist = forms.CharField(widget=None, help_text='By Course Number', required=False)
    course_names_datalist = forms.CharField(widget=None, help_text='By Course Name', required=False)
    section_codes_datalist = forms.CharField(widget=None, help_text='By Section Code', required=False)
    terms_datalist = forms.CharField(widget=None, help_text='By Term', required=False)
    instructors_datalist = forms.CharField(widget=None, help_text='By Instructor', required=False)

    def __init__(self, *args, **kwargs):
        super(MasterBondSectionFilterForm, self).__init__(*args, **kwargs)
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
