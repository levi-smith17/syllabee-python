from core.views import get_environs
from django.core.exceptions import ImproperlyConfigured
from django.views.generic.base import ContextMixin
from editor.models import MasterSyllabus, Profile
from portfolio.models import Portfolio, PortfolioReview, PortfolioSettings


class PortfolioDownloadPrintContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        try:
            context['portfolio'] = Portfolio.objects.get(pk=self.kwargs['pk'])
            context['portfolio_settings'] = PortfolioSettings.objects.get(coordinator=context['portfolio'].section.instructor)
            context['instructor'] = Profile.objects.get(pk=context['portfolio'].section.instructor.id)
            context['reviews'] = PortfolioReview.objects.filter(portfolio=context['portfolio'])
            context['master_syllabus'] = MasterSyllabus.objects.filter(term__section=context['internship'].section)
        except (Portfolio.DoesNotExist, MasterSyllabus.DoesNotExist):
            raise ImproperlyConfigured('Unable to retrieve the print view for the requested portfolio.')
        return {**context, **environs}
