from ..block import BlockForm
from editor.models import *


class ResponseBlockForm(BlockForm):
    def __init__(self, *args, **kwargs):
        self.segment_id = kwargs.pop('segment_id')
        super(ResponseBlockForm, self).__init__(*args, **kwargs)

    class Meta:
        model = ResponseBlock
        exclude = ('type', 'owner', 'max_attempts', 'max_points',)


class ResponseBlockPropertiesForm(BlockForm):
    def __init__(self, *args, **kwargs):
        self.segment_id = kwargs.pop('segment_id')
        super(ResponseBlockPropertiesForm, self).__init__(*args, **kwargs)

    class Meta:
        model = ResponseBlock
        fields = ('max_attempts', 'max_points',)
