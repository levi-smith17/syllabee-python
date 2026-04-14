from ..block import PrintableBlockForm
from django.forms import ModelChoiceField
from editor.models import *


class GradeDeterminationBlockForm(PrintableBlockForm):
    schedule = ModelChoiceField(queryset=None, required=False,
                                help_text=GradeDeterminationBlock._meta.get_field('schedule').help_text)

    def __init__(self, *args, **kwargs):
        super(GradeDeterminationBlockForm, self).__init__(*args, **kwargs)
        self.fields['name'].initial = 'Grade Determination'
        self.fields['description'].widget.attrs['style'] = 'height: 10rem;'
        self.fields['schedule'].queryset = ScheduleBlock.objects.filter(bond__segment_id=self.segment_id)

    class Meta:
        model = GradeDeterminationBlock
        exclude = ('full_screen', 'type', 'owner', 'published', 'permalink',)
