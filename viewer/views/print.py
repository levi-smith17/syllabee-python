from .funcs import get_context_print, get_master_syllabus_and_section
from .mixins import CompleteProgressAccessMixin
from ..forms.print import PrintConfirmationForm
from core.views.funcs import get_environs
from django.db.models import Q
from django.urls import reverse
from django.views.generic import FormView, TemplateView
from editor.models import Segment


class PrintIndexView(CompleteProgressAccessMixin, TemplateView):
    template_name = 'viewer/print/index.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = get_context_print(self.request, **kwargs)
        return {**context, **environs}


class PrintConfirmationView(CompleteProgressAccessMixin, FormView):
    form_class = PrintConfirmationForm
    template_name = 'viewer/print/modal.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        master_syllabus, section = get_master_syllabus_and_section(**self.kwargs)
        q_objects = Q()
        q_objects.add(Q(printing_optional=True), Q.AND)
        q_objects.add(Q(masterbond__master_syllabus=master_syllabus), Q.AND)
        q_objects_or = Q()
        q_objects_or.add(Q(masterbond__masterbondsection__section=None), Q.AND)
        q_objects_or.add(Q(masterbond__masterbondsection__section=section), Q.OR)
        context['modal'] = {}
        context['modal']['message'] = 'Please select optional content to print from the list below. Any required ' \
                                      'content will be included regardless.'
        if master_syllabus.interactive_view:
            context['modal']['url'] = reverse('viewer:print:confirm', args=(self.kwargs['section_hash'],))
        else:
            context['modal']['url'] = reverse('viewer:print:confirm', args=(self.kwargs['course_code'],
                                                                           self.kwargs['section_code'],
                                                                           self.kwargs['term_code']))
        context['modal']['segments'] = Segment.objects.filter(q_objects & q_objects_or)
        return {**context, **environs}

    def get_success_url(self):
        master_syllabus, section = get_master_syllabus_and_section(**self.kwargs)
        if master_syllabus.interactive_view:
            return reverse('viewer:print:index', args=(self.kwargs['section_hash'],))
        else:
            return reverse('viewer:print:index', args=(self.kwargs['course_code'], self.kwargs['section_code'],
                                                      self.kwargs['term_code']))

    def post(self, request, *args, **kwargs):
        if 'segments[]' in request.POST:
            request.session['print_segments'] = request.POST.getlist('segments[]')
        return super(PrintConfirmationView, self).post(request, **kwargs)