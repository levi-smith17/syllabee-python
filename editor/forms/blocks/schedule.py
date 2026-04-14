from ..block import PrintableBlockForm
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField
from django.forms.widgets import NumberInput
from editor.models import *


class ScheduleBlockForm(PrintableBlockForm):
    class Meta:
        model = ScheduleBlock
        exclude = ('owner', 'full_screen', 'type', 'schedule', 'published', 'permalink')


class TopicModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.assignment_name


class OverrideForm(forms.ModelForm):
    assignment = TopicModelChoiceField(queryset=None, help_text=Override._meta.get_field('assignment').help_text)
    due_date = forms.DateField(widget=NumberInput(attrs={'type': 'date'}),
                               help_text=Override._meta.get_field('due_date').help_text)
    due_time = forms.TimeField(widget=NumberInput(attrs={'type': 'time'}), initial=datetime.time(23, 59, 0),
                               required=False, help_text=Override._meta.get_field('due_time').help_text)

    def __init__(self, *args, **kwargs):
        self.master_syllabus_id = kwargs.pop('master_syllabus_id')
        self.segment_id = kwargs.pop('segment_id')
        self.schedule_id = kwargs.pop('schedule_id')
        self.user = kwargs.pop('user')
        super(OverrideForm, self).__init__(*args, **kwargs)
        self.fields['assignment'].queryset = ScheduleTopic.objects.filter(unit__schedule_id=self.schedule_id,
                                                                          assignment_name__isnull=False)

    def clean_due_date(self):
        try:
            data = self.cleaned_data['due_date']
            master_section = (MasterBondSection.objects
                              .filter(master_bond__master_syllabus_id=self.master_syllabus_id,
                                      master_bond__segment_id=self.segment_id, section__isnull=False).first())
            try:
                if master_section.section.term.start_date <= data <= master_section.section.term.end_date:
                    return data
                else:
                    raise ValidationError('The provided due date does not fall within this section\'s term.')
            except AttributeError:
                raise ValidationError('Schedule blocks require valid sections associated with this segment to add an '
                                      'override. Add a valid section to this segment or remove invalid sections and '
                                      'then try again.')
        except MasterBond.DoesNotExist:
            raise ValidationError('The requested master bond does not exist.')

    class Meta:
        model = Override
        exclude = ('owner', 'section',)


class OverrideCreateForm(OverrideForm):
    def __init__(self, *args, **kwargs):
        self.master_syllabus_id = kwargs.get('master_syllabus_id')
        self.segment_id = kwargs.get('segment_id')
        self.schedule_id = kwargs.get('schedule_id')
        self.user = kwargs.get('user')
        super(OverrideCreateForm, self).__init__(*args, **kwargs)
        excluded_overrides = Override.objects.filter(assignment__unit__schedule_id=self.schedule_id) \
            .values('assignment')
        self.fields['assignment'].queryset = (ScheduleTopic.objects
                                              .filter(unit__schedule_id=self.schedule_id, assignment_name__isnull=False)
                                              .exclude(id__in=excluded_overrides))

    class Meta:
        model = Override
        exclude = ('owner', 'section',)


class OverrideDeleteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.master_syllabus_id = kwargs.pop('master_syllabus_id')
        self.segment_id = kwargs.pop('segment_id')
        self.schedule_id = kwargs.pop('schedule_id')
        self.user = kwargs.pop('user')
        super(OverrideDeleteForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Override
        exclude = ('assignment', 'due_date', 'due_time', 'section', 'owner', 'section',)
