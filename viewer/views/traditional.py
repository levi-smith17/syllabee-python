from .funcs import get_context_traditional, get_master_syllabus_and_section, get_syllabus_title
from .mixins import ViewAccessMixin
from core.views.funcs import get_environs, get_loader_context
from django.db.models import Q
from django.urls import reverse
from django.views.generic import TemplateView
from editor.models import Bond


class TraditionalContentView(ViewAccessMixin, TemplateView):
    template_name = 'viewer/traditional/content.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context.update(get_context_traditional(self.request, **kwargs))
        return {**context, **environs}


class TraditionalIndexView(ViewAccessMixin, TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context.update(get_context_traditional(self.request, **kwargs))
        content_toc_json = ('{"course_code": "' + context['section'].course.course_code.lower() +
                            '", "section_code": "' + context['section'].section_code.lower() +
                            '", "term_code": "' + context['section'].term.term_code.lower() + '"}')
        profile_json = ('{"instructor_id": "' + str(context['instructor'].id) + '", "master_syllabus_id": "' +
                        str(context['master_syllabus'].id) + '"}')
        context.update(get_loader_context(content='', stage=content_toc_json, profile=profile_json,
                                          toc=content_toc_json, title=get_syllabus_title(context['section']),
                                          view='traditional', url=reverse('viewer:traditional:syllabus',
                                                                          args=(context['section'].course.course_code.lower(),
                                                                                context['section'].section_code.lower(),
                                                                                context['section'].term.term_code.lower(),))))
        return {**context, **environs}


class TraditionalSegmentView(ViewAccessMixin, TemplateView):
    template_name = 'viewer/traditional/segments.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        try:
            master_syllabus, section = get_master_syllabus_and_section(**kwargs)
        except Exception:
            raise
        context['bonds'] = (Bond.objects
                            .filter(Q(segment__id=self.kwargs['segment_id'], block__printableblock__isnull=False))
                            .exclude((Q(block__printableblock__fileblock__coursesyllabusblock__course__isnull=False) &
                                      ~Q(block__printableblock__fileblock__coursesyllabusblock__course=(section
                                                                                                        .course))) |
                                     (Q(block__printableblock__scheduleblock__isnull=False) &
                                      ~Q(block__printableblock__scheduleblock__schedule__term_length=(section
                                                                                                      .term.length))))
                            .order_by('order'))
        context['master_syllabus'] = master_syllabus
        context['term'] = section.term
        return {**context, **environs}


class TraditionalTocView(ViewAccessMixin, TemplateView):
    template_name = 'viewer/traditional/toc.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context.update(get_context_traditional(self.request, **kwargs))
        return {**context, **environs}
