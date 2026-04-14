from ..block import PrintableBlockForm
from django import forms
from editor.models import *


class ListBlockForm(PrintableBlockForm):
    class Meta:
        model = ListBlock
        exclude = ('full_screen', 'type', 'owner', 'published', 'permalink', 'list_type', 'ordered_type',
                   'ordered_start', 'print_group',)


class ListBlockItemForm(forms.ModelForm):
    parent_item = forms.ModelChoiceField(required=False, queryset=ListBlockItem.objects.all(),
                                         help_text=ListBlockItem._meta.get_field('parent_item').help_text)

    def __init__(self, *args, **kwargs):
        self.block_id = kwargs.pop('block_id')
        self.user = kwargs.pop('user')
        super(ListBlockItemForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs['style'] = 'height: 10rem;'
        self.fields['parent_item'].queryset = ListBlockItem.objects.filter(list_block_id=self.block_id)

    class Meta:
        model = ListBlockItem
        exclude = ('owner', 'list_block', 'order',)


class ListBlockItemDeleteForm(forms.ModelForm):
    class Meta:
        model = ListBlockItem
        exclude = ('owner', 'list_block', 'content', 'order', 'parent_item',)


class ListBlockPropertiesForm(PrintableBlockForm):
    class Meta:
        model = ListBlock
        exclude = ('full_screen', 'type', 'owner', 'published', 'permalink', 'name', 'print_heading',)
