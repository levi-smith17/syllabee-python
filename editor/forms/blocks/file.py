from ..block import BlockUpdateForm
from editor.models import *


class FileBlockForm(BlockUpdateForm):
    def __init__(self, *args, **kwargs):
        super(FileBlockForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs['style'] = 'height: 10rem;'

    class Meta:
        model = FileBlock
        exclude = ('full_screen', 'type', 'owner', 'published', 'permalink',)
