from .mixins import PortfolioDownloadPrintContextMixin
from ..forms import PortfolioForm, PortfolioDeleteForm
from ..models import Portfolio, PortfolioReview
from core.views.funcs import get_cbv_context, get_environs
from core.views.mixins import DeleteViewFormMixin, FormInvalidMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Group, User
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView, View
from django.views.generic.base import ContextMixin
from weasypdf.views import WeasypdfView


class PortfolioContextMixin(ContextMixin, View):
    def get_success_url(self):
        if 'pk' in self.kwargs:
            return reverse('portfolio:detail', args=(self.kwargs['pk'],))
        else:
            return reverse('portfolio:detail')


class PortfolioCreateView(PermissionRequiredMixin, FormInvalidMixin, PortfolioContextMixin, CreateView):
    permission_required = ('portfolio.add_portfolio',)
    model = Portfolio
    form_class = PortfolioForm
    template_name = 'core/offcanvas/add.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['add_url'] = reverse('portfolio:create')
        context['callback'] = 'done_load_regions'
        context['target'] = '#content-container'
        return {**context, **environs}

    def get_form_kwargs(self):
        kwargs = super(PortfolioCreateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        user = User.objects.get(pk=self.object.student.id)
        group = Group.objects.get(name='portfolio_creators')
        # Add the student to the interns group
        if user and group:
            user.groups.add(group)
            user.save()
        return super().form_valid(form)


class PortfolioDeleteView(PermissionRequiredMixin, FormInvalidMixin, DeleteViewFormMixin, DeleteView):
    permission_required = ('portfolio.delete_portfolio',)
    model = Portfolio
    form_class = PortfolioDeleteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['callback'] = 'done_load_regions'
        context['modal']['target'] = '#content-container'
        context['modal']['url'] = reverse('portfolio:delete', args=(self.kwargs['pk'],))
        user = User.objects.get(pk=self.object.student.id)
        group = Group.objects.get(name='portfolio_creators')
        # Remove the student from the interns group
        if user and group:
            user.groups.remove(group)
            user.save()
        return context

    def get_success_url(self):
        return reverse('portfolio:detail')


class PortfolioFeedback:
    pass


class PortfolioDetailView(PermissionRequiredMixin, TemplateView):
    permission_required = ('portfolio.view_portfolio',)
    model = Portfolio
    template_name = 'portfolio/card.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        if 'pk' in self.kwargs:
            try:
                portfolio = Portfolio.objects.get(pk=self.kwargs['pk'])
                self.request.session['portfolio_id'] = portfolio.id
            except Portfolio.DoesNotExist:
                portfolio = 0
        else:
            try:
                portfolio = Portfolio.objects.get(pk=self.request.session.get('portfolio_id'))
            except Portfolio.DoesNotExist:
                portfolio = 0
        context['portfolio'] = portfolio
        if portfolio:
            context['reviews'] = PortfolioReview.objects.filter(portfolio=portfolio)
        return {**context, **environs}


class PortfolioDownloadView(PermissionRequiredMixin, PortfolioDownloadPrintContextMixin, WeasypdfView):
    permission_required = ('portfolio.view_portfolio',)
    body_template_name = 'portfolio/journal/print/index.html'
    header_template_name = ''
    footer_template_name = ''
    styles_template_name = 'weasypdf/print.scss'
    title = 'Portfolio Journal'


class PortfolioPrintView(PermissionRequiredMixin, PortfolioDownloadPrintContextMixin, TemplateView):
    permission_required = ('portfolio.view_portfolio',)
    template_name = 'portfolio/print/index.html'


class PortfolioUpdateView(PermissionRequiredMixin, FormInvalidMixin, PortfolioContextMixin, UpdateView):
    permission_required = ('portfolio.change_portfolio',)
    model = Portfolio
    form_class = PortfolioForm
    template_name = 'core/offcanvas/edit.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['callback'] = 'done_load_regions'
        context['delete_url'] = None
        context['edit_url'] = reverse('portfolio:update', args=(self.object.id,))
        context['target'] = '#content-container'
        user = User.objects.get(pk=self.object.student.id)
        group = Group.objects.get(name='portfolio_creators')
        # Add the student to the interns group
        if user and group:
            user.groups.add(group)
            user.save()
        return {**context, **environs}

    def get_form_kwargs(self):
        kwargs = super(PortfolioUpdateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs
