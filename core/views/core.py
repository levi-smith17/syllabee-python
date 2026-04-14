from internship.models import InternshipSettings
from .mixins import FormInvalidMixin
from .funcs import get_environs, get_loader_context, handler403, handler404, lti_auth_user
from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import TemplateView, FormView
from editor.models import Section, MasterSyllabus
from lti_tool.utils import get_launch_from_request
from lti_tool.views import LtiLaunchBaseView
from pylti1p3.deep_link_resource import DeepLinkResource
from pylti1p3.lineitem import LineItem
from viewer.views.funcs import get_total_points_possible, is_complete_total, create_or_update_section_progress

from ..forms import LtiDeepLinkForm


class IndexView(TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        context['editable'] = True
        context.update(get_loader_context(title='Syllabus Search', view='search',
                                          url=reverse('core:index')))
        return {**context, **environs}


class CopyrightVersionView(TemplateView):
    template_name = 'core/offcanvas/copyright_version.html'

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        changelog = open(str(settings.BASE_DIR) + '/CHANGELOG.md', mode='r')
        context['changelog'] = ('<textarea class="border-secondary rounded text-bg-dark w-100" rows="12">' +
                                changelog.read() + '</textarea>')
        changelog.close()
        context['copyright_notice'] = ('<strong>&copy; 2021-' + str(environs['current_year']) +
                                       '</strong> by Levi Smith under the General Public License version 3.0. '
                                       'You can view the details of this license below. If you have any questions, '
                                       'please contact me at <a href="mailto:lsmith2@edisonohio.edu" '
                                       'class="link-dark">lsmith2@edisonohio.edu</a>.')
        gpl_license = open(str(settings.BASE_DIR) + '/LICENSE', mode='r')
        context['gpl_license'] = ('<textarea class="border-secondary rounded text-bg-dark w-100" rows="12">' +
                                  gpl_license.read() + '</textarea>')
        gpl_license.close()
        context['version_info'] = ('The changelog for ' + environs['app_name'] +
                                   ' can be found below. The latest updates can be found and accessed via GitHub (use '
                                   'the button below to view this project on GitHub). Please use GitHub to submit an '
                                   'issue if your are experiencing any problems with ' + environs['app_name'] +
                                   ' or have suggestions for new features.')
        return {**context, **environs}


@method_decorator(xframe_options_exempt, name='dispatch')
class LtiDeepLinkView(PermissionRequiredMixin, FormInvalidMixin, FormView):
    permission_required = ('editor.view_mastersyllabus',)
    form_class = LtiDeepLinkForm
    template_name = 'core/lti/deep_link.html'

    def form_valid(self, form):
        lti_launch = get_launch_from_request(self.request, form.cleaned_data['lti_launch_id'])
        message_launch = lti_launch.get_message_launch()
        if not message_launch.is_deep_link_launch():
            return handler403(self.request, 'Unsupported request! Must be a deep link launch!')
        master_bond_section = form.cleaned_data['section']
        section_hash = master_bond_section.section.hash
        launch_url = self.request.build_absolute_uri(reverse('lti'))
        # Create the quick link to the syllabus (students must have completed it before they can access it through
        # this link).
        resource_link = DeepLinkResource()
        (resource_link.set_url(launch_url)
         .set_custom_params({'section_hash': section_hash, 'link': 'syllabus'})
         .set_title('Syllabus'))
        # Create the LineItem for the grade.
        max_points = get_total_points_possible(section_hash)
        line_item = LineItem()
        line_item.set_tag('grade').set_score_maximum(max_points).set_label('Syllabee Activity')
        launch_url = self.request.build_absolute_uri(reverse('lti'))
        # Create the graded resource.
        resource_activity = DeepLinkResource()
        (resource_activity.set_url(launch_url)
         .set_custom_params({'section_hash': section_hash, 'link': 'graded'})
         .set_title('Syllabee Activity')
         .set_lineitem(line_item))
        if master_bond_section.section.format == 'Internship':
            # Create the LineItem for the grade.
            internship_settings = InternshipSettings.objects.filter().first()
            line_item = LineItem()
            line_item.set_tag('grade').set_score_maximum(internship_settings.journal_points).set_label('Internship Journal')
            launch_url = self.request.build_absolute_uri(reverse('lti'))
            # Create the graded resource.
            resource_journal = DeepLinkResource()
            (resource_journal.set_url(launch_url)
             .set_custom_params({'section_hash': section_hash, 'link': 'internship'})
             .set_title('Internship Journal')
             .set_lineitem(line_item))
            html = message_launch.get_deep_link().output_response_form([resource_link, resource_activity, resource_journal])
        else:
            html = message_launch.get_deep_link().output_response_form([resource_link, resource_activity])
        return HttpResponse(html)

    def get_context_data(self, **kwargs):
        environs = get_environs(self.request)
        context = super().get_context_data(**kwargs)
        return {**context, **environs}

    def get_form_kwargs(self):
        kwargs = super(LtiDeepLinkView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        kwargs.update({'lti_launch_id': None})
        return kwargs


@method_decorator(xframe_options_exempt, name='dispatch')
class ApplicationLaunchView(LtiLaunchBaseView):
    def handle_resource_launch(self, request, lti_launch):
        if lti_launch.is_present:
            lti_auth_user(request, lti_launch)
            section_hash = lti_launch.get_custom_claim('section_hash')
            #stuff = lti_launch.context.id_on_platform

            if section_hash:
                section = Section.objects.get(hash=section_hash)
                master_syllabus = MasterSyllabus.objects.get(masterbond__masterbondsection__section=section)
                link = lti_launch.get_custom_claim('link')
                if link == 'internship':
                    return HttpResponseRedirect(reverse('internship:index'))
                elif link == 'graded':
                    if master_syllabus.interactive_view:
                        create_or_update_section_progress(self.request, master_syllabus, section,
                                                          lti_launch.get_launch_id())
                        return HttpResponseRedirect(reverse('viewer:interactive:syllabus',
                                                            args=(section_hash,)))
                    else:
                        return HttpResponseRedirect(reverse('viewer:traditional:syllabus',
                                                            args=(section.course.course_code.lower(),
                                                                  section.section_code.lower(),
                                                                  section.term.term_code.lower())))
                else:
                    if master_syllabus.interactive_view:
                        complete = is_complete_total(self.request, section)
                        if complete or self.request.user.groups.filter(name='instructors'):
                            return HttpResponseRedirect(reverse('viewer:interactive:syllabus',
                                                                args=(section_hash,)))
                        else:
                            return handler403(self.request, 'You must complete the syllabus activity before '
                                                            'you can access it using this link.')
                    else:
                        return HttpResponseRedirect(reverse('viewer:traditional:syllabus',
                                                            args=(section.course.course_code.lower(),
                                                                  section.section_code.lower(),
                                                                  section.term.term_code.lower())))
            else:
                return handler404(self.request)
        else:
            return handler403(self.request, 'No LTI launch data found. Please close this window and retry.')

    def handle_deep_linking_launch(self, request, lti_launch):
        if lti_launch.is_present:
            lti_auth_user(request, lti_launch)
            message_launch = lti_launch.get_message_launch()
            if not message_launch.is_deep_link_launch():
                return handler403(request, 'Unsupported request! Must be a deep link launch!')
            environs = get_environs(self.request)
            form_data = {'user': self.request.user, 'lti_launch_id': lti_launch.get_launch_id()}
            context = {'editable': False, 'form': LtiDeepLinkForm(**form_data),
                       'lti_launch_id': lti_launch.get_launch_id(), 'title': 'Syllabee'}
            return render(request, 'core/lti/deep_link.html', {**context, **environs})
        else:
            return handler403(self.request, 'No LTI launch data found. Please close this window and retry.')

