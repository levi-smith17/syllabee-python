from .funcs import (check_response, create_or_get_progress, get_attempts_remaining, get_bond_progress_previous,
                    get_bond_progress_next, get_context_interactive, get_master_syllabus_and_section, get_progress,
                    get_syllabus_title, get_total_points, has_optional_segments, is_syllabus_visible,
                    get_total_points_possible)
from .mixins import BondProgressAccessMixin, CompleteProgressAccessMixin, PreCompleteProgressAccessMixin
from ..models import BondProgress, MasterBondProgress, SectionProgress
from core.views.funcs import get_loader_context, get_environs
from datetime import datetime
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.urls import reverse
from django.views.generic import DetailView, TemplateView
from editor.models import Bond
from lti_tool.utils import get_launch_from_request
from pylti1p3.grade import Grade


class InteractiveBondView(PermissionRequiredMixin, BondProgressAccessMixin, DetailView):
    permission_required = 'viewer.change_bondprogress'
    model = BondProgress

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        master_syllabus, section = get_master_syllabus_and_section(**self.kwargs)
        section_progress = SectionProgress.objects.get(section=section, student=self.request.user)
        response_correct = None
        bond_progress = BondProgress.objects.get(pk=self.kwargs['pk'])
        bond_progress_prev = get_bond_progress_previous(section_progress, bond_progress)
        bond_progress_next = get_bond_progress_next(section_progress, bond_progress)
        if self.extra_context['clicked'] == 'check':
            response_correct = check_response(self.request, master_syllabus, bond_progress)
            if master_syllabus.prohibit_backtracking:
                bond_progress_prev = None
            attempts_remaining = get_attempts_remaining(master_syllabus, bond_progress)
            if not response_correct and attempts_remaining[0] > 0:
                bond_progress_next = bond_progress
        if self.extra_context['clicked'] == 'next' and not bond_progress.master_bond_progress.start_time:
            bond_progress.master_bond_progress.start_time = datetime.now()
            bond_progress.master_bond_progress.save()
        if self.extra_context['clicked'] == 'next':
            if bond_progress_prev:
                if bond_progress.master_bond_progress != bond_progress_prev.master_bond_progress:
                    master_bond_progress = MasterBondProgress.objects.get(pk=bond_progress_prev.master_bond_progress.id)
                    if not master_bond_progress.completed:
                        master_bond_progress.stop_time = datetime.now()
                        master_bond_progress.points = get_total_points(master_bond_progress)
                        master_bond_progress.completed = True
                        master_bond_progress.save()
            if bond_progress_prev and not bond_progress_prev.completed:
                bond_progress_prev.stop_time = datetime.now()
                bond_progress_prev.completed = True
                bond_progress_prev.save()
            if not bond_progress.start_time:
                bond_progress.start_time = datetime.now()
                bond_progress.save()
        attempts_remaining = get_attempts_remaining(master_syllabus, bond_progress)
        mbp, bp, progress_percentage, total_points = get_progress(section_progress)
        context = {'attempts_remaining': attempts_remaining[0], 'attempts_remaining_str': attempts_remaining[1],
                   'bond_progress': bond_progress, 'master_syllabus': master_syllabus,
                   'progress_percentage': progress_percentage, 'next': bond_progress_next,
                   'previous': bond_progress_prev, 'response_correct': response_correct, 'section': section,
                   'term': section.term, 'total_points': total_points,
                   'visible': is_syllabus_visible(self.request, master_syllabus, section)}
        return {**context, **environs}

    def get_template_names(self):
        if hasattr(self.object.bond.block, 'printableblock'):
            return ['viewer/interactive/card/printable.html']
        else:
            return ['viewer/interactive/card/response.html']


class InteractiveButtonView(PermissionRequiredMixin, DetailView):
    permission_required = 'viewer.change_bondprogress'
    model = BondProgress
    template_name = 'viewer/interactive/buttons/toc.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        master_syllabus, section = get_master_syllabus_and_section(**self.kwargs)
        bond_progress = BondProgress.objects.get(pk=self.kwargs['pk'])
        context = {'bond_progress': bond_progress, 'master_syllabus': master_syllabus, 'section': section}
        return {**context, **environs}


class InteractiveCompleteView(PermissionRequiredMixin, PreCompleteProgressAccessMixin, TemplateView):
    permission_required = 'viewer.change_sectionprogress'
    template_name = 'viewer/interactive/content/complete.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context.update(get_context_interactive(self.request, **kwargs))
        section_progress, master_bond_progresses, bond_progresses = create_or_get_progress(self.request,
                                                                                           context['master_syllabus'],
                                                                                           context['section'])
        mbp, bp, progress_percentage, total_points = get_progress(section_progress)
        try:
            if section_progress.lti_launch_id:
                max_points = get_total_points_possible(section_progress.section.hash)
                lti_launch = get_launch_from_request(self.request, section_progress.lti_launch_id)
                launch = lti_launch.get_message_launch()
                ags = launch.get_ags()
                gr = Grade()
                (gr.set_score_given(total_points)
                .set_score_maximum(max_points)
                .set_timestamp(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+0000'))
                .set_activity_progress('Completed')
                .set_grading_progress('FullyGraded')
                .set_user_id(lti_launch.user.sub))
                line_item = ags.find_lineitem('label', 'Syllabee Activity')
                ags.put_grade(gr, line_item)
            if not section_progress.completed:
                section_progress.points = total_points
                section_progress.stop_time = datetime.now()
                section_progress.completed = True
                section_progress.save()
        except:
            raise TypeError('We were unable to send your grade back to Blackboard. Please contact your instructor.')
        context.update({'master_bond_progresses': master_bond_progresses, 'view': 'complete'})
        return {**context, **environs}


class InteractiveContentView(PermissionRequiredMixin, TemplateView):
    permission_required = 'viewer.change_bondprogress'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context.update(get_context_interactive(self.request, **kwargs))
        section_progress, master_bond_progresses, bond_progresses = create_or_get_progress(self.request,
                                                                                           context['master_syllabus'],
                                                                                           context['section'], True)
        context.update({'master_bond_progresses': master_bond_progresses, 'view': 'complete'})
        return {**context, **environs}

    def get_template_names(self):
        return ['viewer/interactive/content/complete.html']


class InteractiveEndView(PermissionRequiredMixin, TemplateView):
    permission_required = 'viewer.change_bondprogress'
    template_name = 'viewer/interactive/card/end.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        master_syllabus, section = get_master_syllabus_and_section(**self.kwargs)
        section_progress = SectionProgress.objects.get(section=section, student=self.request.user)
        master_bond_progress, bond_progress, progress_percentage, total_points = get_progress(section_progress)
        if master_bond_progress:
            if not master_bond_progress.completed:
                master_bond_progress.stop_time = datetime.now()
                master_bond_progress.completed = True
                master_bond_progress.save()
        if bond_progress:
            if not bond_progress.completed:
                bond_progress.stop_time = datetime.now()
                bond_progress.completed = True
                bond_progress.save()
        context = {'master_syllabus': master_syllabus, 'next': None, 'previous': bond_progress,
                   'progress_percentage': progress_percentage, 'section': section, 'term': section.term,
                   'total_points': total_points, 'visible': is_syllabus_visible(self.request, master_syllabus, section)}
        return {**context, **environs}


class InteractiveIndexView(PermissionRequiredMixin, TemplateView):
    permission_required = 'viewer.change_bondprogress'
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context.update(get_context_interactive(self.request, **kwargs))
        section_progress, master_bond_progresses, bond_progresses = create_or_get_progress(self.request,
                                                                                           context['master_syllabus'],
                                                                                           context['section'], True)
        context.update({'master_bond_progresses': master_bond_progresses})
        content_toc_json = ('{"section_hash": "' + context['section'].hash + '"}')
        profile_json = ('{"instructor_id": "' + str(context['instructor'].id) + '", "master_syllabus_id": "' +
                        str(context['master_syllabus'].id) + '"}')
        if section_progress.completed == 1 or section_progress.section.instructor == self.request.user:
            stage = content_toc_json
            view = 'complete'
        else:
            stage = ''
            view = 'interactive'
        context.update(get_loader_context(content=content_toc_json, stage=stage, profile=profile_json,
                                          toc=content_toc_json, title=get_syllabus_title(context['section']), view=view,
                                          url=reverse('viewer:interactive:syllabus', args=(context['section'].hash,))))
        return {**context, **environs}


class InteractiveSegmentView(PermissionRequiredMixin, CompleteProgressAccessMixin, TemplateView):
    permission_required = ('viewer.change_bondprogress',)
    raise_exception = True
    template_name = 'viewer/interactive/content/segment.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        master_syllabus, section = get_master_syllabus_and_section(**kwargs)
        context['block_only'] = False
        context['bonds'] = (Bond.objects
                            .filter(Q(segment__id=self.kwargs['segment_id'], block__printableblock__isnull=False))
                            .exclude((Q(block__printableblock__scheduleblock__isnull=False) &
                                      ~Q(block__printableblock__scheduleblock__schedule__term_length=(section
                                                                                                      .term.length))))
                            .order_by('order'))
        context['master_syllabus'] = master_syllabus
        context['term'] = section.term
        return {**context, **environs}


class InteractiveStartView(PermissionRequiredMixin, TemplateView):
    permission_required = 'viewer.change_bondprogress'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        master_syllabus, section = get_master_syllabus_and_section(**self.kwargs)
        section_progress, master_bond_progresses, bond_progresses = create_or_get_progress(self.request,
                                                                                           master_syllabus,
                                                                                           section)
        master_bond_progress, bond_progress, progress_percentage, total_points = get_progress(section_progress)
        if self.kwargs['view']:
            view = self.kwargs['view']
        else:
            view = 'complete' if section.instructor == self.request.user else 'interactive'
        context = {'master_bond_progresses': master_bond_progresses, 'master_syllabus': master_syllabus,
                   'view': view, 'next': bond_progress, 'previous': None,
                   'progress_percentage': progress_percentage, 'section': section, 'term': section.term,
                   'total_points': total_points, 'visible': is_syllabus_visible(self.request, master_syllabus, section)}
        return {**context, **environs}

    def get_template_names(self):
        section_progress = SectionProgress.objects.get(section__hash=self.kwargs['section_hash'],
                                                       student=self.request.user)
        if section_progress.completed == 1:
            # We have a completed SectionProgress object, so jump straight to the complete view
            return ['viewer/interactive/content/complete.html']
        master_bond_progresses = (MasterBondProgress.objects.filter(section_progress=section_progress,
                                                                    completed=False))
        bond_progresses = (BondProgress.objects.filter(master_bond_progress__section_progress=section_progress,
                                                       completed=False))
        if not master_bond_progresses.exists() and not bond_progresses.exists():
            # We have completed all MasterBondProgress and BondProgress objects, but the SectionProgress is not marked
            # as complete yet, so display the end page.
            return ['viewer/interactive/card/end.html']
        master_bond_progresses = (MasterBondProgress.objects.filter(section_progress=section_progress,
                                                                    student=self.request.user,
                                                                    start_time__isnull=False))
        if master_bond_progresses.exists():
            # We have at least one MasterBondProgress object with a start time, so the user isn't new.
            return ['viewer/interactive/card/resume.html']
        return ['viewer/interactive/card/welcome.html']


class InteractiveTocView(PermissionRequiredMixin, TemplateView):
    permission_required = 'viewer.view_bondprogress'
    template_name = 'viewer/interactive/toc/segments.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        master_syllabus, section = get_master_syllabus_and_section(**kwargs)
        section_progress, master_bond_progresses, bond_progresses = create_or_get_progress(self.request,
                                                                                           master_syllabus,
                                                                                           section, True)
        context = {'master_bond_progresses': master_bond_progresses, 'master_syllabus': master_syllabus,
                   'view': self.kwargs['view'], 'print_modal': has_optional_segments(master_syllabus, section),
                   'section': section, 'section_progress': section_progress, 'term': section.term,
                   'visible': is_syllabus_visible(self.request, master_syllabus, section)}
        return {**context, **environs}
