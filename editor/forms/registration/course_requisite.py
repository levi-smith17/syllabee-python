from ...models import Course, CourseRequisite, REQUISITE_TYPES
from core.widgets import DatalistWidget
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError, Q


class CourseRequisiteForm(forms.ModelForm):
    requisite_course = forms.CharField(widget=None,
                                       help_text=CourseRequisite._meta.get_field('requisite_course').help_text)
    requisite_type = forms.ChoiceField(initial=True, choices=REQUISITE_TYPES,
                                 help_text=CourseRequisite._meta.get_field('requisite_type').help_text)

    def __init__(self, *args, **kwargs):
        super(CourseRequisiteForm, self).__init__(*args, **kwargs)
        self.fields['requisite_course'].widget = DatalistWidget(model=Course, filters=(Q(inactive=False)),
                                                      attrs={'disabled': False, 'required': True})

    class Meta:
        model = CourseRequisite
        exclude = ('order', 'requisite_block',)

    def clean_requisite_course(self):
        try:
            data = self.cleaned_data['requisite_course'].split(' - ')
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


class CourseRequisiteDeleteForm(forms.Form):
    class Meta:
        model = CourseRequisite
        exclude = '__all__'
