from core.views.funcs import (get_cbv_context, get_environs, get_lbv_context, get_objects, reset_pagination,
                              update_pagination)
from core.views.mixins import FormInvalidMixin, ListViewContextMixin, SearchViewContextMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, ListView, TemplateView, View
from django.views.generic.base import ContextMixin
from editor.models import MasterBondSection, Profile
from editor.forms.master_bond_section import MasterBondSectionFilterForm
from editor.views.master_bond_section import MasterBondSectionFilterFormMixin


class SearchContextMixin(ContextMixin, View):
    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super(SearchContextMixin, self).get_context_data(**kwargs)
        context['filters'] = self.request.session.get('masterbondsection_filters', None)
        context['pattern'] = self.request.session.get('masterbondsection_pattern', None)
        context['items'] = get_objects(MasterBondSection, self.request.user, context['filters'],
                                       context['pattern'])
        context['title'] = 'Syllabus Search'
        context['model'] = 'masterbondsection'
        context = update_pagination(self, context)
        return {**context, **environs}


class SearchClearView(SearchContextMixin, TemplateView):
    template_name = 'viewer/search/syllabi.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super(SearchContextMixin, self).get_context_data(**kwargs)
        if 'masterbondsection_filters' in self.request.session:
            del self.request.session['masterbondsection_filters']
        if 'masterbondsection_pattern' in self.request.session:
            del self.request.session['masterbondsection_pattern']
        context['filters'] = None
        context['pattern'] = None
        context['items'] = None
        context['title'] = 'Syllabus Search'
        context['model'] = 'masterbondsection'
        reset_pagination(self.request, context['model'], True, True)
        context = update_pagination(self, context)
        return {**context, **environs}


class SearchDetailView(SearchContextMixin, TemplateView):
    template_name = 'viewer/search/syllabi.html'


class SearchInstructorResultsView(ListViewContextMixin, ListView):
    model = Profile

    def get_template_names(self):
        return ['viewer/search/instructors.html']


class SearchInstructorSearchView(SearchViewContextMixin, ListView):
    model = Profile

    def get_template_names(self):
        return ['viewer/search/instructors.html']


class SearchSyllabusFilterView(FormInvalidMixin, MasterBondSectionFilterFormMixin, FormView):
    model = MasterBondSection
    form_class = MasterBondSectionFilterForm
    template_name = 'core/offcanvas/filter.html'
    success_url = reverse_lazy('viewer:search:results')

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super(SearchSyllabusFilterView, self).get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context = get_lbv_context(self, context)
        context['filter_url'] = reverse('viewer:search:filter')
        context['target'] = '#content-container'
        reset_pagination(self.request, context['model'], False, True)
        context = update_pagination(self, context)
        return {**context, **environs}


class SearchSyllabusResultsView(ListViewContextMixin, ListView):
    model = MasterBondSection

    def get_template_names(self):
        return ['viewer/search/syllabi.html']


class SearchSyllabusSearchView(SearchViewContextMixin, ListView):
    model = MasterBondSection

    def get_template_names(self):
        return ['viewer/search/syllabi.html']
