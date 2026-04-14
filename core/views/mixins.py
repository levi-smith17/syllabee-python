from .funcs import get_cbv_context, get_environs, get_lbv_context, get_modal, handler_form, reset_pagination, \
    update_pagination
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured
from django.views.generic import View
from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormMixin
from django.urls import reverse


class DeleteViewFormMixin(FormMixin, View):
    template_name = 'core/modal/confirmation.html'

    def form_valid(self, form):
        try:
            return super().form_valid(self.get_form())
        except Exception as e:
            return handler_form(self.request, exceptions={'exceptions': {repr(e)}})

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['modal'] = get_modal(message='Are you sure you want to delete the following ' +
                                             context['verbose_name'] + '? ' +
                                             self.model.delete_warning() + ' This operation cannot be undone.',
                                     message_alert_css='', message_type='warning', operation='deleted',
                                     target='#content-container')
        return {**context, **environs}


class GroupsRequiredMixin(UserPassesTestMixin):
    groups_required = None

    def get_groups_required(self):
        if self.groups_required is None:
            raise ImproperlyConfigured(
                f'{self.__class__.__name__} is missing the '
                f'groups_required attribute. Define '
                f'{self.__class__.__name__}.groups_required, or override '
                f'{self.__class__.__name__}.get_groups_required.'
            )
        if isinstance(self.groups_required, str):
            groups = (self.groups_required,)
        else:
            groups = self.groups_required
        return groups

    def has_groups(self):
        groups = self.get_groups_required()
        return self.request.user.groups.filter(name__in=groups).exists()

    def dispatch(self, request, *args, **kwargs):
        if not self.has_groups():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class FilterViewFormMixin(FormMixin, View):
    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        context['filter_url'] = reverse(context['module'] + ':registration:' + context['model'] + ':filter')
        reset_pagination(self.request, context['model'], False, True)
        context = get_lbv_context(self, context)
        context = update_pagination(self, context)
        return {**context, **environs}


class FormInvalidMixin(FormMixin, View):
    def form_invalid(self, form):
        return handler_form(self.request, exceptions=form.errors)


class ListViewContextMixin(ContextMixin, View):
    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        if 'filter_key' in self.kwargs:
            reset_pagination(self.request, context['model'], False, True)
            filters = self.request.session.get(context['model'] + '_filters', None)
            del filters[self.kwargs['filter_key']]
            self.request.session.modified = True
        context = get_lbv_context(self, context)
        context = update_pagination(self, context)
        return {**context, **environs}


class SearchViewContextMixin(ContextMixin, View):
    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context = get_cbv_context(self, context)
        self.request.session[context['model'] + '_pattern'] = self.request.GET.get('pattern', None)
        reset_pagination(self.request, context['model'], True, False)
        context = get_lbv_context(self, context)
        context = update_pagination(self, context)
        return {**context, **environs}
