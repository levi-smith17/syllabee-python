from ..models import *
from core.widgets import DatalistWidget
from editor.forms.registration.course import clean_course_generic
from django import forms
from django.forms import NumberInput


class GenericCreateForm(forms.ModelForm):
    course = forms.CharField(widget=None)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(GenericCreateForm, self).__init__(*args, **kwargs)
        self.fields['course'].widget = DatalistWidget(model=Course, filters=(Q(inactive=False)),
                                                      attrs={'disabled': False, 'required': False})

    def clean_course(self):
        return clean_course_generic(self)


class ScheduleForm(forms.ModelForm):
    course = forms.CharField(widget=None, help_text=Schedule._meta.get_field('course').help_text)
    display_units_column = forms.ChoiceField(initial=False, choices=BOOLEAN_CHOICES,
                                      help_text=Schedule._meta.get_field('display_units_column').help_text)
    assignment_due_time = forms.TimeField(widget=NumberInput(attrs={'type': 'time'}), initial=datetime.time(23, 59, 0),
                                          help_text=Schedule._meta.get_field('assignment_due_time').help_text)
    finals_due_time = forms.TimeField(widget=NumberInput(attrs={'type': 'time'}), initial=datetime.time(23, 59, 0),
                                      help_text=Schedule._meta.get_field('finals_due_time').help_text)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(ScheduleForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs['style'] = 'height: 10rem;'
        self.fields['course'].widget = DatalistWidget(model=Course, filters=(Q(inactive=False)),
                                                      attrs={'disabled': False, 'required': False})

    def clean_course(self):
        return clean_course_generic(self)

    class Meta:
        model = Schedule
        exclude = ('owner',)


class ScheduleCreateForm(ScheduleForm, GenericCreateForm):
    course = forms.CharField(widget=None, help_text=Schedule._meta.get_field('course').help_text)

    class Meta:
        model = Schedule
        exclude = ('owner',)


class ScheduleCopyForm(forms.Form):
    from_schedule = forms.ModelChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        self.schedule_id = kwargs.pop('schedule_id')
        super(ScheduleCopyForm, self).__init__(*args, **kwargs)
        self.fields['from_schedule'].queryset = Schedule.objects.all().exclude(id=self.schedule_id)


class ScheduleDeleteForm(forms.Form):
    class Meta:
        model = Schedule
        exclude = '__all__'


class ScheduleTopicForm(forms.ModelForm):
    week = forms.ChoiceField(choices=[(0, 0)], help_text=ScheduleTopic._meta.get_field('week').help_text)
    emphasize_topic = forms.ChoiceField(initial=False, choices=BOOLEAN_CHOICES,
                                        help_text=ScheduleTopic._meta.get_field('emphasize_topic').help_text)
    emphasize_assignment = forms.ChoiceField(initial=False, choices=BOOLEAN_CHOICES,
                                             help_text=ScheduleTopic._meta.get_field('emphasize_assignment').help_text)
    assignment_category = forms.CharField(widget=None, required=False, help_text=(ScheduleTopic._meta
                                                                                  .get_field('assignment_category')
                                                                                  .help_text))

    def __init__(self, *args, **kwargs):
        self.schedule_id = kwargs.pop('schedule_id')
        self.user = kwargs.pop('user')
        super(ScheduleTopicForm, self).__init__(*args, **kwargs)
        schedule = Schedule.objects.get(pk=self.schedule_id)
        self.fields['week'].choices = [(x, x) for x in range(1, schedule.term_length.num_weeks + 1)]
        self.fields['assignment_category'].widget = DatalistWidget(model=ScheduleTopic,
                                                                   filters=(Q(unit__schedule__id=self.schedule_id) &
                                                                            Q(assignment_category__isnull=False)),
                                                                   values='assignment_category',
                                                                   attrs={'disabled': False, 'required': False})

    class Meta:
        model = ScheduleTopic
        exclude = ('owner',)


class ScheduleTopicDeleteForm(forms.Form):
    class Meta:
        model = ScheduleTopic
        exclude = '__all__'


class ScheduleUnitForm(forms.ModelForm):
    week = forms.ChoiceField(help_text=ScheduleUnit._meta.get_field('week').help_text)

    def __init__(self, *args, **kwargs):
        self.schedule_id = kwargs.pop('schedule_id')
        super(ScheduleUnitForm, self).__init__(*args, **kwargs)
        schedule = Schedule.objects.get(pk=self.schedule_id)
        self.fields['week'].choices = [(x, x) for x in range(1, schedule.term_length.num_weeks + 1)]

    class Meta:
        model = ScheduleUnit
        exclude = ('schedule', 'owner',)


class ScheduleUnitDeleteForm(forms.Form):
    class Meta:
        model = ScheduleUnit
        exclude = '__all__'
