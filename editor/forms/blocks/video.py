from ..block import BlockUpdateForm
from editor.models import *


class VideoBlockForm(BlockUpdateForm):
    def __init__(self, *args, **kwargs):
        super(VideoBlockForm, self).__init__(*args, **kwargs)
        self.fields['embed_code'].widget.attrs['style'] = 'height: 10rem;'
        self.fields['content_verbose'].widget.attrs['style'] = 'height: 10rem;'

    class Meta:
        model = VideoBlock
        exclude = ('full_screen', 'type', 'owner', 'published', 'permalink',)
