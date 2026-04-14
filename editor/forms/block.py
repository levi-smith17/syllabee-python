from ..models import *
from core.widgets import DatalistWidget
from django import forms


class BlockForm(forms.ModelForm):
    class Meta:
        model = Block
        exclude = ('owner', 'name', 'type', 'effective_term',)


class BlockUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.segment_id = kwargs.pop('segment_id')
        super(BlockUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Block
        exclude = ('owner',)


class PrintableBlockForm(forms.ModelForm):
    print_group = forms.CharField(widget=None, required=False,
                                  help_text=PrintableBlock._meta.get_field('print_group').help_text)

    def __init__(self, *args, **kwargs):
        self.segment_id = kwargs.pop('segment_id')
        super(PrintableBlockForm, self).__init__(*args, **kwargs)
        self.fields['print_group'].widget = DatalistWidget(model=Block, filters=(Q(bond__segment_id=self.segment_id) &
                                                                    Q(printableblock__print_group__isnull=False)),
                                                           values='printableblock__print_group',
                                                           attrs={'disabled': False, 'required': False})

    class Meta:
        model = Block
        exclude = ('owner', 'permalink', 'published',)


class PrintableBlockPublishForm(forms.ModelForm):
    class Meta:
        model = PrintableBlock
        exclude = ('name', 'type', 'full_screen', 'print_group', 'print_heading', 'published', 'permalink', 'owner',)
