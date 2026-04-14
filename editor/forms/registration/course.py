from ...models import *
from core.widgets import DatalistWidget
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError

def clean_course_generic(form):
    try:
        data = form.cleaned_data['course'].split(' - ')
        course = Course.objects.get(course_code=data[0], name=data[1])
        if course.inactive:
            raise ValidationError('The provided course is inactive. Please select an active course from the list.')
        return course
    except Course.DoesNotExist:
        raise ValidationError('The provided course does not exist. Please select a valid course from the list.')
    except IndexError:
        raise ValidationError('The provided input is invalid. Please select a valid course from the list.')
    except ProtectedError as e:
        raise ValidationError(str(e))


class CourseForm(forms.ModelForm):
    inactive = forms.ChoiceField(initial=False, choices=BOOLEAN_CHOICES,
                                 help_text=Course._meta.get_field('inactive').help_text)

    class Meta:
        model = Course
        exclude = ('course_code', 'owner',)


class CourseCreateForm(forms.ModelForm):
    class Meta:
        model = Course
        exclude = ('course_code', 'inactive', 'owner',)


class CourseDeleteForm(forms.Form):
    class Meta:
        model = Course
        exclude = '__all__'


class CourseFilterForm(forms.Form):
    course_prefixes_datalist = forms.CharField(widget=None, help_text='By Course Prefix', required=False)

    def __init__(self, *args, **kwargs):
        super(CourseFilterForm, self).__init__(*args, **kwargs)
        self.fields['course_prefixes_datalist'].widget = DatalistWidget(model=Course, filters=(Q(inactive=False)),
                                                                        values='prefix',
                                                                        attrs={'disabled': False, 'required': False})


class CourseRenameForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('future_name',)
