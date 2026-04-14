from ..block import PrintableBlockForm
from django import forms
from editor.models import *


class TableBlockForm(PrintableBlockForm):
    class Meta:
        model = TableBlock
        exclude = ('full_screen', 'type', 'owner', 'published', 'permalink', 'number_of_columns', 'accent',
                   'borders', 'caption_position', 'caption', 'has_group_dividers', 'print_group',)


class TableBlockCreateForm(PrintableBlockForm):
    class Meta:
        model = TableBlock
        exclude = ('full_screen', 'type', 'owner', 'published', 'permalink',)


class TableBlockPropertiesForm(PrintableBlockForm):
    has_group_dividers = forms.ChoiceField(initial=False, required=False, choices=BOOLEAN_CHOICES,
                                           help_text=TableBlock._meta.get_field('has_group_dividers').help_text)

    class Meta:
        model = TableBlock
        exclude = ('full_screen', 'type', 'owner', 'published', 'permalink', 'name', 'print_heading',)


class TableBlockColumnForm(forms.ModelForm):
    class Meta:
        model = TableBlockColumn
        exclude = ('owner', 'table', 'column_number', 'span', )


class TableBlockRowForm(forms.ModelForm):
    class Meta:
        model = TableBlockRow
        exclude = ('owner', 'table')


class TableBlockRowDeleteForm(forms.ModelForm):
    class Meta:
        model = TableBlockRow
        fields = ()
