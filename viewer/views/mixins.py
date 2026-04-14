from ..forms import ResetProgressConfirmationForm
from ..models import BondProgress, MasterBondProgress, SectionProgress
from .funcs import get_master_syllabus_and_section, is_complete, is_complete_total
from core.views.funcs import get_environs, get_modal
from datetime import date
from django.contrib.auth.mixins import AccessMixin, PermissionRequiredMixin
from django.views.generic import FormView


class BondProgressAccessMixin(AccessMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        master_syllabus, section = get_master_syllabus_and_section(**kwargs)
        bond_progress = BondProgress.objects.get(pk=kwargs['pk'])
        if master_syllabus.prohibit_backtracking and bond_progress.completed:
            self.prohibit_backtracking = True
            return self.handle_no_permission()
        elif not bond_progress.start_time:
            if self.extra_context['clicked'] != 'next':
                self.prohibit_backtracking = False
                return self.handle_no_permission()
            else:
                return super(BondProgressAccessMixin, self).dispatch(request, *args, **kwargs)
        else:
            return super(BondProgressAccessMixin, self).dispatch(request, *args, **kwargs)

    def get_permission_denied_message(self):
        if self.prohibit_backtracking:
            self.permission_denied_message = ('Accessing completed blocks is prohibited. You can only access the '
                                              'currently displayed block.')
        else:
            self.permission_denied_message = 'You can\'t do that. You must progress through the syllabus in order.'
        return self.permission_denied_message


class CompleteProgressAccessMixin(AccessMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name__in=('admins', 'instructors')).exists():
            master_syllabus, section = get_master_syllabus_and_section(**kwargs)
            if master_syllabus.interactive_view and not is_complete_total(request, section):
                self.permission_denied_message = 'You can only access the complete view of this syllabus once you ' \
                                                 'complete the interactive version.'
                return self.handle_no_permission()
        return super(CompleteProgressAccessMixin, self).dispatch(request, *args, **kwargs)


class PreCompleteProgressAccessMixin(AccessMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        master_syllabus, section = get_master_syllabus_and_section(**kwargs)
        if not is_complete(request, section):
            return self.handle_no_permission()
        else:
            return super(PreCompleteProgressAccessMixin, self).dispatch(request, *args, **kwargs)

    def get_permission_denied_message(self):
        self.permission_denied_message = 'It looks like you have some blocks that are not complete (they are missing ' \
                                         'a green check mark next to them in the Table of Contents). Load each block ' \
                                         'that hasn\'t been completed, review it, and then click the Next button to ' \
                                         'mark it as completed.'
        return self.permission_denied_message


class ProgressResetMixin(PermissionRequiredMixin, FormView):
    permission_required = 'viewer.delete_sectionprogress'
    form_class = ResetProgressConfirmationForm
    template_name = 'core/modal/confirmation.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        student = SectionProgress.objects.get(section__hash=self.kwargs['section_hash'],
                                              student=self.kwargs['student_id']).student
        context['callback'] = 'done_reset'
        context['modal'] = get_modal(message=f'Are you sure you want to reset <strong>{student.first_name} '
                                             f'{student.last_name}\'s</strong> progress? Any progress associated with '
                                             f'a segment that applies to all sections will also be reset (across all '
                                             f'sections). This operation cannot be undone.',
                                     message_alert_css='m-0', message_type='warning', operation='reset',
                                     target='#syllabus-content',
                                     url='')
        context['object'] = None
        context['verbose_name'] = 'Progress'
        return {**context, **environs}

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            master_syllabus, section = get_master_syllabus_and_section(**kwargs)
            section_progress = SectionProgress.objects.get(section=section, student=kwargs['student_id'])
            master_bond_progresses = MasterBondProgress.objects.filter(section_progress=section_progress)
            bond_progresses = BondProgress.objects.filter(master_bond_progress__section_progress=section_progress)
            for bond_progress in bond_progresses:
                bond_progress.delete()
            for master_bond_progress in master_bond_progresses:
                master_bond_progress.delete()
            section_progress.delete()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ViewAccessMixin(AccessMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        master_syllabus, section = get_master_syllabus_and_section(**kwargs)
        if not request.user.groups.filter(name__in=('admins', 'instructors')):
            if master_syllabus.interactive_view and date.today() < master_syllabus.term.end_date:
                return self.handle_no_permission()
        return super(ViewAccessMixin, self).dispatch(request, *args, **kwargs)

    def get_permission_denied_message(self):
        self.permission_denied_message = ('The requested syllabus is restricted to interactive view only. You must '
                                          'access this syllabus via your institution\'s learning management system '
                                          '(e.g., Blackboard, Canvas, etc.)')
        return self.permission_denied_message
