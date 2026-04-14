from core.views.funcs import get_environs, get_loader_context, handler404
from django.urls import reverse
from django.views.generic import TemplateView, View
from django.views.generic.base import ContextMixin
from editor.models import Bond, MasterSyllabus, Profile


class BlockMixin(ContextMixin, View):
    def dispatch(self, request, *args, **kwargs):
        bond = (Bond.objects
                .filter(owner__username=self.kwargs['instructor'], block__printableblock__isnull=False,
                        block__printableblock__published=True,
                        block__printableblock__permalink=self.kwargs['permalink']))
        if bond.count() == 0:
            return handler404(request)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        bond = (Bond.objects
                .filter(owner__username=self.kwargs['instructor'], block__printableblock__isnull=False,
                        block__printableblock__published=True,
                        block__printableblock__permalink=self.kwargs['permalink'])
                .order_by('block_id')
                .last())
        instructor = Profile.objects.get(user__username=self.kwargs['instructor'])
        context['bond'] = bond
        context['bonds'] = (bond,)
        context['editable'] = True
        context['instructor'] = instructor
        context['master_bonds'] = None
        context['visible'] = True
        master_syllabus_id = self.request.session.get('master_syllabus_id', None)
        if master_syllabus_id:
            context['master_syllabus'] = MasterSyllabus.objects.get(pk=master_syllabus_id)
        else:
            context['master_syllabus'] = (MasterSyllabus.objects
                                          .filter(owner__username=instructor,
                                                  term__start_date__exact=environs['current_term'].start_date)
                                          .first())
        content_toc_json = '{"instructor": "' + self.kwargs['instructor'] + '", "permalink": "' + self.kwargs[
            'permalink'] + '"}'
        context.update(get_loader_context(content=content_toc_json,
                                          profile='{"instructor_id": "' + str(instructor.id) + '"}',
                                          toc=content_toc_json, title=bond.block.name, view='block',
                                          url=reverse('viewer:block:index', args=(self.kwargs['instructor'],
                                                                                 self.kwargs['permalink'],))))
        return {**context, **environs}


class BlockIndexView(BlockMixin, TemplateView):
    template_name = 'core/index.html'


class BlockContentView(BlockMixin, TemplateView):
    template_name = 'viewer/block/content.html'


class BlockPrintView(BlockMixin, TemplateView):
    template_name = 'viewer/print/index.html'


class BlockTocView(BlockMixin, TemplateView):
    template_name = 'viewer/block/toc.html'
