from ..block import PrintableBlockForm
from editor.models import *


class CourseSyllabusBlockForm(PrintableBlockForm):
    def __init__(self, *args, **kwargs):
        super(CourseSyllabusBlockForm, self).__init__(*args, **kwargs)
        self.fields['description'].initial = 'The Part I Syllabus provides the description, goals, and topics for ' \
                                             'the course. This portion of the syllabus is developed by the various ' \
                                             'faculty within the department and put before the college\'s curriculum ' \
                                             'committee for review and approval to ensure that it meets the ' \
                                             'college\'s high standards and core values. Students should acquaint ' \
                                             'themselves with the Part I Syllabus to understand the purpose of the ' \
                                             'course and what they are expected to learn from it.'
        self.fields['description'].widget.attrs['style'] = 'height: 10rem;'
        self.fields['course'].queryset = Course.objects.filter(inactive=False)

    class Meta:
        model = CourseSyllabusBlock
        exclude = ('full_screen', 'type', 'owner', 'published', 'permalink',)
