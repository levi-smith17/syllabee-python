from ..forms import PortfolioReviewForm, PortfolioReviewDeleteForm
from ..models import PortfolioReview
from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, UpdateView, View
from django.views.generic.base import ContextMixin


class PortfolioReviewContextMixin(ContextMixin, View):
    def get_success_url(self):
        return reverse('portfolio:detail', args=(self.kwargs['portfolio_id'],))


class PortfolioReviewCreateView(PermissionRequiredMixin, FormInvalidMixin, PortfolioReviewContextMixin,
                                   CreateView):
    permission_required = ('portfolio.add_portfolioreview',)
    model = PortfolioReview
    form_class = PortfolioReviewForm
    template_name = 'core/offcanvas/add.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('portfolio:review:create', args=(self.kwargs['portfolio_id'],))
        context['callback'] = 'done_load_regions'
        context['target'] = '#content-container'
        return {**context, **environs}

    def get_form_kwargs(self):
        kwargs = super(PortfolioReviewCreateView, self).get_form_kwargs()
        kwargs.update({'portfolio_id': self.kwargs['portfolio_id']})
        return kwargs


class PortfolioReviewDeleteView(PermissionRequiredMixin, FormInvalidMixin, DeleteViewFormMixin,
                                PortfolioReviewContextMixin, DeleteView):
    permission_required = ('portfolio.delete_portfolioreview',)
    model = PortfolioReview
    form_class = PortfolioReviewDeleteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['callback'] = 'done_load_regions'
        context['modal']['target'] = '#content-container'
        context['modal']['url'] = reverse('portfolio:review:delete',
                                          args=(self.kwargs['portfolio_id'], self.kwargs['pk'],))
        return context


class PortfolioReviewUpdateView(PermissionRequiredMixin, FormInvalidMixin, PortfolioReviewContextMixin, UpdateView):
    permission_required = ('portfolio.change_portfolioreview',)
    model = PortfolioReview
    form_class = PortfolioReviewForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['callback'] = 'done_load_regions'
        context['delete_url'] = None
        context['edit_url'] = reverse('portfolio:review:update',
                                      args=(self.kwargs['portfolio_id'], self.object.id,))
        context['target'] = '#content-container'
        return {**context, **environs}

    def get_form_kwargs(self):
        kwargs = super(PortfolioReviewUpdateView, self).get_form_kwargs()
        kwargs.update({'portfolio_id': self.kwargs['portfolio_id']})
        return kwargs
