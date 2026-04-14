import json, random, string
from datetime import date, datetime
from django.apps import apps
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse
from editor.models import Branding, MasterBondSection, MasterSyllabus, QuickLink, Profile, Term


PAGINATOR = 15  # The number of records to display per page when pagination is in effect.


def get_cbv_context(self, context):
    """
    Returns a dictionary representing a generic context for a Django Class-Based View.

    Parameters:
    :param (View) self:             The Class-Based View to update the context of.
    :param (dict) context:          The context being built so far.

    Returns:
    :return (dict)                  - An updated context dictionary.
    """
    if not context:
        context = {}
    context['module'] = self.model._meta.app_label
    context['model'] = self.model._meta.model_name
    context['verbose_name'] = self.model._meta.verbose_name
    context['verbose_name_plural'] = self.model._meta.verbose_name_plural
    context['filterable'] = self.model.filterable
    context['add_perm'] = self.request.user.has_perm(context['module'] + '.add_' + context['model'])
    context['change_perm'] = self.request.user.has_perm(context['module'] + '.change_' + context['model'])
    context['delete_perm'] = self.request.user.has_perm(context['module'] + '.delete_' + context['model'])
    context['view_perm'] = self.request.user.has_perm(context['module'] + '.view_' + context['model'])
    context['callback'] = 'done_generic'
    context['content_id'] = ''
    context['delete_url'] = False
    context['edit_message'] = False
    context['next_url'] = False
    context['target'] = False
    context['title'] = None
    return context


def get_current_term():
    """
    Returns a Term object representing the current term (based on today's date).

    Returns:
    :return (Term)          - Returns a Term object.
    """
    current_term = Term.objects.filter(Q(start_date__lte=date.today()) & Q(end_date__gte=date.today()))
    if not current_term:
        return Term.objects.filter(Q(start_date__gte=date.today()) &
                                   (Q(term_code__endswith='FS') | Q(term_code__endswith='SS') |
                                    Q(term_code__endswith='US') | Q(term_code__endswith='FL') |
                                    Q(term_code__endswith='SL'))).order_by('start_date').first()
    return current_term[0] if current_term else None


def get_environs(request, environs=None):
    """
    Builds and returns all necessary environment variables for use across the entire app.

    Parameters:
    :param (Request) request:   The request object to retrieve user and session data.
    :param (dict) environs:     The environs that are being built or updated.

    Returns:
    :return (dict)              - Returns a dictionary representing environment variables.
    """
    if not environs:
        environs = {}
    environs = get_environs_branding(environs)
    environs['current_term'] = get_current_term()
    environs['font_size'] = request.session.get('font', '14')
    if request.user.groups.filter(name='instructors'):
        environs['master_syllabi'] = MasterSyllabus.objects.filter(owner=request.user, term__archived=False)
    environs['restricted_quicklinks'] = QuickLink.objects.filter(restricted=True)
    return environs


def get_environs_branding(environs=None):
    """
    Builds and returns all necessary environment variables for use across the entire app that are specific to branding.

    Parameters:
    :param (dict) environs:     The environs that are being built or updated.

    Returns:
    :return (dict)              - Returns a dictionary representing branding environment variables.
    """
    if not environs:
        environs = {}
    branding = Branding.objects.get(pk=1)
    environs['branding'] = {}
    environs['branding']['institution'] = branding.institution
    environs['branding']['background_image'] = branding.background_image.name
    environs['branding']['core_values'] = branding.core_values
    environs['profile'] = {}
    environs['app_name'] = settings.APP_NAME
    environs['current_year'] = datetime.today().year
    environs['font_size'] = 14
    environs['quicklinks'] = QuickLink.objects.filter(restricted=False)
    environs['version'] = settings.VERSION
    return environs


def get_loader_context(content='', stage='', profile='', toc='', title='Syllabus Search', view='search', url=''):
    """
    Returns a dictionary representing the variables necessary to load a page.

    Parameters:
    :param (str) content:   A string representing JSON for the content region of the page.
    :param (str) stage:     A string representing JSON for staging the content region of the page.
    :param (str) profile:   A string representing JSON for the profile region of the page.
    :param (str) toc:       A string representing JSON for the toc region of the page.
    :param (str) title:     A string representing the page title.
    :param (str) view:      A string used to determine which JSON loader to use.
    :param (str) url:       The URL to return to when the page is reloaded.

    Returns:
    :return (dict)          - A dictionary containing the variables necessary to load a page.
    """
    url = reverse('core:index') if not url else url
    return {'json_content_string': content, 'json_stage_string': stage, 'json_profile_string': profile,
            'json_toc_string': toc, 'json_view': view, 'reload_url': url, 'title': title}


def get_loader_json(target, viewname, *args):
    """
    Returns a JSON object for use in loading a region of the page.

    Parameters:
    :param (str) target:        A string representing the region target on the DOM.
    :param (str) viewname:      A string representing a viewname for use with reverse(). Must be a valid URL viewname.

    Returns:
    :return (JSON)              - A JSON object for use in loading a region of the page.
    """
    return json.dumps({target: reverse(viewname, args=args)})


def get_lbv_context(self, context):
    """
    Returns a dictionary representing a generic context for a Django ListView.

    Parameters:
    :param (ListView) self:         The ListView to update the context of.
    :param (dict) context:          The context being built so far.

    Returns:
    :return (dict)                  - An updated context dictionary.
    """
    context['filters'] = self.request.session.get(context['model'] + '_filters', None)
    context['pattern'] = self.request.session.get(context['model'] + '_pattern', None)
    context['items'] = get_objects(self.model, self.request.user,
                                   self.request.session.get(context['model'] + '_filters', None), context['pattern'])
    context['target'] = '#content-container'
    return context


def get_modal(message='', message_alert_css='', message_type='', operation=False, target=False, submit_icon='',
              submit_text='', url=False, ajax=True, next=False):
    """
    Retrieves a dictionary containing the various components necessary for a modal. All parameters are optional.

    Parameters:
    :param (str) message:           The message to be included within the modal.
    :param (str) message_alert_css: Any CSS needing to be applied to the message box.
    :param (str) message_type:      The type of message to be displayed. Should be either 'info', 'warning', or
                                    'danger'.
    :param (str) operation:         The type of operation being performed by the modal (e.g., added, deleted, etc.).
    :param (str) target:         The ID of the HTML container where the result of the modal's action should be
                                    placed.
    :param (str) submit_icon:       The icon used by the submit button for this modal. Must be a valid Bootstrap icon
                                    identifier.
    :param (str) submit_text:       The text displayed on the submit button for this modal.
    :param (str) url:               The URL of the action to be taken by the modal (if any).
    :param (Boolean) ajax:          Whether this modal should operate via ajax or not.
    :param (str) next:              An optional URL to redirect to after the modal has been submitted.

    Returns:
    :return (dict)                  - Returns a dictionary object containing the settings for the modal.
    """
    return {'ajax': ajax, 'message': message, 'message_alert_css': message_alert_css,
            'message_type': ('info' if message and not message_type else message_type), 'operation': operation,
            'next': next, 'target': target, 'submit_icon': submit_icon, 'submit_text': submit_text, 'url': url}


def get_model(request, model, environs):
    """
    Retrieves a model based on a user's permissions. Includes a collection of items from this model based on the user's
    permissions.

    Parameters:
    :param (Request) request:   The request object to retrieve user and session data.
    :param (object) model:      The model to be retrieved.
    :param (dict) environs:     A dictionary of environment variables for use throughout this app.

    Returns:
    :return (dict)              - Returns a dictionary object containing the module name, model name, a collection of
                                items, user permissions, and any other required business logic.
    """
    environs['models'] = (environs['models'] if 'models' in environs else [])
    module_name = model._meta.app_label
    module_verbose_name = apps.get_app_config(module_name).verbose_name
    model_name = model._meta.model_name
    environs['models'].append({'module': module_name, 'module_verbose': module_verbose_name.lower(), 'name': model_name,
                               'filterable': model.filterable, 'verbose_name': model._meta.verbose_name,
                               'verbose_name_plural': model._meta.verbose_name_plural,
                               'add_perm': request.user.has_perm(module_name+'.add_'+model_name),
                               'view_perm': request.user.has_perm(module_name + '.view_' + model_name)})
    return environs


def get_objects(model, user, filters=None, pattern=None):
    """
    Returns a queryset containing objects of the requested model type.

    Parameters:
    :param (object) model:          The model to retrieve objects from.
    :param (User) user:             The user object to limit results to.
    :param (dict) filters:          If filtering, contains a dictionary of filters to use in retrieving a queryset.
    :param (string) pattern:        If conducting a search, the pattern to search for.

    Returns:
    :return (object)                - Returns a collection of objects.
    """
    q_objects = Q()
    if hasattr(model, 'get_exclusions'):
        exclusions = model.get_exclusions(user)
        if exclusions:
            q_objects.add(exclusions, Q.AND)
    previous_key = None
    if filters:
        for key, value in filters.items():
            key = key.split('-')
            if previous_key == key[0]:
                q_objects.add(Q(('%s' % key[0], value)), Q.OR)
            else:
                q_objects.add(Q(('%s' % key[0], value)), Q.AND)
            previous_key = key[0]
        if not user.groups.filter(name__in=('admins', 'instructors')) and model == MasterBondSection:
            q_objects.add((Q(section__term__archived=True) |
                           Q(master_bond__master_syllabus__interactive_view=False)), Q.AND)
        return model.objects.filter(q_objects) or None
    elif pattern:
        if not user.groups.filter(name__in=('admins', 'instructors')) and model == MasterBondSection:
            return (model.objects
                    .search(pattern, user)
                    .exclude(Q(section__term__archived=False) &
                             Q(master_bond__master_syllabus__interactive_view=True)) or None)
        else:
            return model.objects.search(pattern, user) or None
    else:
        if user.groups.filter(name='students') or not user.is_authenticated or model == MasterBondSection:
            return None
        return model.objects.filter(q_objects) or None


def get_office_hours(instructor, master_syllabus_id=None):
    """
    Retrieves the office hours for the provided instructor. If master_syllabus_id is provided, then the office hours
    for that master syllabus will be retrieved. Otherwise, the office hours for the current term will be retrieved.

    Parameters:
    :param (User) instructor:           The instructor to retrieve office hours for.
    :param (int) master_syllabus_id:    An optional master syllabus identifier that will retrieve its office hours.

    Returns:
    :return (str)                       - Returns a string containing the office hours for an instructor.
    """
    try:
        if master_syllabus_id:
            return MasterSyllabus.objects.get(pk=master_syllabus_id).office_hours
        else:
            term = get_current_term()
            return (MasterSyllabus.objects.filter(owner=instructor, term__start_date__gte=term.start_date,
                                                  term__end_date__lte=term.end_date).first().office_hours)
    except (AttributeError, MasterSyllabus.DoesNotExist, ValueError):
        return '<strong class="fw-bold text-danger">NONE PROVIDED</strong>'


def lti_auth_user(request, lti_launch):
    """
    Retrieves the office hours for the provided instructor. If master_syllabus_id is provided, then the office hours
    for that master syllabus will be retrieved. Otherwise, the office hours for the current term will be retrieved.

    Parameters:
    :param (Request) request:       The request object to retrieve user and session data.
    :param (LtiLaunch) lti_launch:  The LTI launch object to retrieve LTI session data.
    """
    try:
        app_user = User.objects.get(email=lti_launch.user.email)
        # User already exists within Syllabee
        login(request, app_user)
    except User.DoesNotExist:
        # User needs to be created within Syllabee
        new_user = User(username=lti_launch.user.email, first_name=lti_launch.user.given_name,
                        last_name=lti_launch.user.family_name, email=lti_launch.user.email)
        new_user.set_password(''.join([random.choice(string.digits + string.ascii_letters) for i in range(0, 16)]))
        new_user.set_unusable_password()
        new_user.save()
        if lti_launch.membership.is_instructor:
            group = Group.objects.get(name='instructors')
        else:
            group = Group.objects.get(name='students')
        group.user_set.add(new_user)
        login(request, new_user)


def reset_pagination(request, model_name, reset_filters, reset_pattern):
    """
    Resets the session variables that control pagination for a specific model.

    Parameters:
    :param (Request) request:       The request object to retrieve user and session data.
    :param (str) model_name:        The name of the model to reset pagination for.
    :param (bool) reset_filters:    Whether to reset the filters or not.
    :param (bool) reset_pattern:    Whether to reset the pattern or not.

    Returns:
    (void)
    """
    if reset_filters:
        request.session[model_name + '_filters'] = None
    if reset_pattern:
        request.session[model_name + '_pattern'] = None
    request.session[model_name + '_limit_start'] = 0
    request.session[model_name + '_limit_end'] = PAGINATOR
    request.session[model_name + '_page'] = 1
    request.session[model_name + '_total_pages'] = 1


def update_pagination(self, context):
    """
    Updates the pagination information, which allows certain models to be presented with paginated views.

    Parameters:
    :param (View) self:         A View object, which contains session data among other View-specific data.
    :param (dict) context:      The current context, which is updated by this method.

    Returns:
    :return (dict)              - Returns a dictionary object with pagination data added.
    """
    try:
        context['count'] = context['items'].count()
    except AttributeError:
        context['count'] = 0
    limit_start = self.request.session.get(context['model'] + '_limit_start', 0)
    limit_end = self.request.session.get(context['model'] + '_limit_end', PAGINATOR)
    page = self.request.session.get(context['model'] + '_page', 1)
    if 'pagination' in self.kwargs:
        if self.kwargs['pagination'] == 'first' and context['count'] > 0:
            limit_start = 0
            limit_end = PAGINATOR
            page = 1
        if self.kwargs['pagination'] == 'previous' and context['count'] > 0:
            limit_start -= PAGINATOR
            limit_end -= PAGINATOR
            page -= 1
        if self.kwargs['pagination'] == 'next' and limit_end < context['count']:
            limit_start += PAGINATOR
            limit_end += PAGINATOR
            page += 1
    context['limit_start'] = self.request.session[context['model'] + '_limit_start'] = limit_start
    context['limit_end'] = self.request.session[context['model'] + '_limit_end'] = limit_end
    try:
        context['items'] = context['items'][limit_start:limit_end]
    except TypeError:
        pass
    context['page'] = self.request.session[context['model'] + '_page'] = page
    total_pages = (context['count'] // PAGINATOR)
    if context['count'] < PAGINATOR:
        total_pages = 1
    elif context['count'] > (PAGINATOR * total_pages):
        total_pages += 1
    context['total_pages'] = self.request.session[context['model'] + '_total_pages'] = total_pages
    return context


def handler_form(request, exceptions=None):
    """
    Handles form validation errors.

    Parameters:
    :param (Request) request:       The request object to retrieve user and session data.
    :param (dict) exceptions:       A dictionary of exceptions to be presented to the user.

    Returns:
    :return (HttpResponse)          - Returns an HttpResponse object.
    """
    environs = get_environs(request)
    exception_string = '<ul class="my-2">'
    exception_count = 0
    for field, exception in exceptions.items():
        exception_string += '<li>' + ' '.join(exception) + '</li>'
        exception_count += 1
    exception_string += '</ul>'
    plural = 's' if exception_count > 1 else ''
    context = {'code': 400, 'type': 'Bad Request', 'text': 'Uh-oh! We couldn\'t save your changes due to the following '
                                                           'reason' + plural + ': ', 'exception': exception_string}
    return handler_renderer(request, {**context, **environs}, 400)


def handler_message(support_code):
    """
    Returns a standardized handler message with the provided support code.

    Parameters:
    :param (str) support_code:      The support code to be displayed to the user.

    Returns:
    :return (str)                   - Returns a string containing the standardized handler message.
    """
    return ('Please click the version button at the bottom of the left-hand navbar to report this issue, and include '
            'the following issue code when doing so: <strong>' + support_code + '</strong>.')


def handler_response_form(request, response, exception=''):
    """
    Handles form validation errors when checking the response of a question.

    Parameters:
    :param (Request) request:       The request object to retrieve user and session data.
    :param (int) response:          An integer representing an HTTP response code.
    :param (str) exception:         A string representing an exception message.

    Returns:
    :return (HttpResponse)          - Returns an HttpResponse object.
    """
    environs = get_environs(request)
    context = {'code': response, 'exception': exception, 'type': ('Incorrect' if response == 400 else 'Correct')}
    return handler_renderer(request, {**context, **environs}, response)


def handler400(request, exception=''):
    """
    Handles HTTP 400 response errors if there's a bad request.

    Parameters:
    :param (Request) request:       The request object to retrieve user and session data.
    :param (str) exception:         A string representing an exception message.

    Returns:
    return (HttpResponse)          - Returns an HttpResponse object.
    """
    environs = get_environs(request)
    context = {'code': 400, 'exception': 'We couldn\'t understand your request, make some adjustments, and give it '
                                         'another go... ' + str(exception), 'type': 'Bad Request'}
    return handler_renderer(request, {**context, **environs}, 400)


def handler403(request, exception=''):
    """
    Handles HTTP 403 response errors if a user tries to access an area they shouldn't.

    Parameters:
    :param (Request) request:       The request object to retrieve user and session data.
    :param (str) exception:         A string representing an exception message.

    Returns:
    return (HttpResponse)          - Returns an HttpResponse object.
    """
    environs = get_environs(request)
    context = {'code': 403, 'type': 'Forbidden', 'exception': 'Uh oh! ' + str(exception)}
    return handler_renderer(request, {**context, **environs}, 403)


def handler404(request, exception=''):
    """
    Handles HTTP 404 response errors if a user tries to access a page that doesn't exist.

    Parameters:
    :param (Request) request:       The request object to retrieve user and session data.
    :param (str) exception:         A string representing an exception message.

    Returns:
    return (HttpResponse)          - Returns an HttpResponse object.
    """
    environs = get_environs(request)
    context = {'code': 404, 'exception': 'That\'s embarrassing! We must have misplaced that!', 'type': 'Not Found'}
    return handler_renderer(request, {**context, **environs}, 404)


def handler405(request, exception=''):
    """
    Handles HTTP 405 response errors if a user tries to do something that isn't allowed.

    Parameters:
    :param (Request) request:       The request object to retrieve user and session data.
    :param (str) exception:         A string representing an exception message.

    Returns:
    return (HttpResponse)          - Returns an HttpResponse object.
    """
    environs = get_environs(request)
    context = {'code': 405, 'class': 'text-bg-warning', 'exception': exception, 'type': 'Not Allowed'}
    return render(request=request, template_name='core/error/toast.html', context={**context, **environs}, status=405)


def handler500(request, exception=''):
    """
    Handles HTTP 500 response errors if something goes completely south.

    Parameters:
    :param (Request) request:       The request object to retrieve user and session data.
    :param (str) exception:         A string representing an exception message.

    Returns:
    return (HttpResponse)          - Returns an HttpResponse object.
    """
    environs = get_environs(request)
    context = {'code': 500, 'exception': 'That shouldn\'t have happened! ' + str(exception),
               'type': 'Internal Server Error'}
    return handler_renderer(request, {**context, **environs}, 500)


def handler_renderer(request, context, status):
    """
    Handles HTTP response objects depending on the type and whether the request was a normal browser request or an
    AJAX one.

    Parameters:
    :param (Request) request:       The request object to retrieve user and session data.
    :param (dict) context:          The context to be returned with the error message.
    :param (int) status:            An integer representing an HTTP response.

    Returns:
    return (HttpResponse)          - Returns an HttpResponse object.
    """
    context['class'] = 'text-bg-danger'
    if request.accepts('text/html'):
        # We're dealing with a normal browser request.
        return render(request=request, template_name='core/error/index.html', context=context, status=status)
    else:
        # We're dealing with an AJAX request.
        return render(request=request, template_name='core/error/toast.html', context=context, status=status)
