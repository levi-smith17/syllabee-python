from .portfolio import *
from .review import *
from core.views import get_loader_context
from django.core.exceptions import PermissionDenied


class PortfolioIndexView(PermissionRequiredMixin, TemplateView):
    permission_required = 'portfolio.view_portfolio'
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        if self.request.user.groups.filter(name__in=['admins', 'instructors']).exists():
            context = {'editable': True, 'portfolio_id': str(self.request.session.get('portfolio_id', 0))}
            content_json = ('{"portfolio_id": "' + str(self.request.session.get('portfolio_id', 0)) + '"}')
            profile_json = ('{"instructor_id": "' + str(self.request.user.id) + '"}')
            context.update(get_loader_context(content=content_json, profile=profile_json, title='Portfolio Management',
                                              view='portfolio', url=reverse('portfolio:index')))
        else:
            try:
                portfolio = Portfolio.objects.get(intern=self.request.user)
            except Portfolio.DoesNotExist:
                raise PermissionDenied('You are not currently enrolled in a course with a portfolio. Please contact '
                                       'your instructor.')
            context = {'editable': False, 'portfolio_id': portfolio.id}
            content_json = ('{"portfolio_id": "' + str(portfolio.id) + '"}')
            profile_json = ('{"instructor_id": "' + str(portfolio.section.instructor.id) + '"}')
            context.update(get_loader_context(content=content_json, profile=profile_json, title='Portfolio Reviews',
                                              view='portfolio', url=reverse('portfolio:index')))
        return {**context, **environs}


class PortfolioTocView(PermissionRequiredMixin, TemplateView):
    permission_required = 'portfolio.view_portfolio'
    template_name = 'portfolio/toc.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        if self.request.user.groups.filter(name__in=['admins', 'instructors']).exists():
            context['portfolio_id'] = self.request.session.get('portfolio_id', 0)
            context['portfolios'] = Portfolio.objects.filter(section__instructor=self.request.user)
        return {**context, **environs}
