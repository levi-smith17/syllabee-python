import json
from core.views.funcs import handler_message
from django import template
from django.urls import reverse
from viewer.views.funcs import get_segments_interactive, get_segments_traditional


register = template.Library()


@register.simple_tag()
def get_json_stage(json_view, json_string):
    try:
        kwargs = json.loads(json_string) if json_string else {}
    except:
        return json.dumps({'error': {'responseText': {'class': 'danger', 'code': 500, 'text': {'format': 'Invalid JSON string. ' + handler_message('gibbon')}, 'type': 'Internal Server Error'}}})
    if json_view == 'complete':
        return json.dumps({'#content-container': reverse('viewer:interactive:content', args=(kwargs['section_hash'],))})
    elif json_view == 'traditional':
        return json.dumps({'#content-container': reverse('viewer:traditional:content', args=(kwargs['course_code'], kwargs['section_code'], kwargs['term_code'],))})
    elif json_view == 'toc':
        return json.dumps({'#toc-container': reverse('viewer:interactive:toc', args=(kwargs['section_hash'], 'interactive'))})


@register.simple_tag(takes_context=True)
def get_json_content(context, json_view, json_string):
    try:
        kwargs = json.loads(json_string) if json_string else {}
    except:
        return json.dumps({'error': {'responseText': {'class': 'danger', 'code': 500, 'text': {'format': 'Invalid JSON string. ' + handler_message('gibbon')}, 'type': 'Internal Server Error'}}})
    if json_view == 'admin':
        return json.dumps({'#content-container': reverse('editor:registration:' + kwargs['model'] + ':detail')})
    elif json_view == 'block':
        return json.dumps({'#content-container': reverse('viewer:block:content', args=(kwargs['instructor'], kwargs['permalink'],))})
    elif json_view == 'complete':
        return get_segments_interactive(context['request'], kwargs['section_hash'])
    elif json_view == 'curriculum':
        if 'program_id' in kwargs and int(kwargs['program_id']) > 0:
            return json.dumps({'#content-container': reverse('curriculum:program:detail', args=(kwargs['program_id'],))})
        else:
            return json.dumps({'#content-container': reverse('curriculum:content')})
    elif json_view == 'editor':
        if 'segment_id' in kwargs and int(kwargs['segment_id']) > 0:
            return json.dumps({'#content-container': reverse('editor:mastersyllabus:segment:detail', args=(kwargs['master_syllabus_id'], kwargs['segment_id'],))})
        else:
            return json.dumps({'#content-container': reverse('editor:mastersyllabus:segment:detail', args=(kwargs['master_syllabus_id'],))})
    elif json_view == 'end':
        return json.dumps({'#content-container': reverse('viewer:interactive:complete', args=(kwargs['section_hash'],))})
    elif json_view == 'interactive':
        return json.dumps({'#content-container': reverse('viewer:interactive:start', args=(kwargs['section_hash'], json_view,))})
    elif json_view == 'interactive_block':
        return json.dumps({'#content-container': reverse('viewer:interactive:block', args=(kwargs['section_hash'], kwargs['bond_progress_id'],))})
    elif json_view == 'internship':
        if 'internship_id' in kwargs and int(kwargs['internship_id']) > 0:
            return json.dumps({'#content-container': reverse('internship:journal:detail', args=(kwargs['internship_id'],))})
        else:
            return json.dumps({'#content-container': reverse('internship:journal:detail')})
    elif json_view == 'lock':
        return json.dumps({'#master-syllabi': reverse('editor:mastersyllabus:list')})
    elif json_view == 'messages':
        if 'message_id' in kwargs and int(kwargs['message_id']) > 0:
            return json.dumps({'#content-container': reverse('editor:mastersyllabus:message:detail', args=(kwargs['master_syllabus_id'], kwargs['message_id'],))})
        else:
            return json.dumps({'#content-container': reverse('editor:mastersyllabus:message:detail', args=(kwargs['master_syllabus_id'],))})
    elif json_view == 'portfolio':
        if 'portfolio_id' in kwargs and int(kwargs['portfolio_id']) > 0:
            return json.dumps({'#content-container': reverse('portfolio:detail', args=(kwargs['portfolio_id'],))})
        else:
            return json.dumps({'#content-container': reverse('portfolio:detail')})
    elif json_view == 'progress':
        if 'section_id' in kwargs:
            return json.dumps({'#content-container': reverse('editor:mastersyllabus:progress:detail', args=(kwargs['master_syllabus_id'], kwargs['section_id'],))})
        else:
            return json.dumps({'#content-container': reverse('editor:mastersyllabus:progress:dashboard', args=(kwargs['master_syllabus_id'],))})
    elif json_view == 'traditional':
        return get_segments_traditional(context['request'], **kwargs)
    else:
        return json.dumps({'#content-container': reverse('viewer:search:detail')})


@register.simple_tag()
def get_json_profile(json_string):
    try:
        kwargs = json.loads(json_string) if json_string else {}
    except:
        return json.dumps({'error': {'responseText': {'class': 'danger', 'code': 500, 'text': {'format': 'Invalid JSON string. ' + handler_message('bonobo')}, 'type': 'Internal Server Error'}}})
    if 'instructor_id' in kwargs and 'master_syllabus_id' in kwargs:
        return json.dumps({'#profile-container': reverse('editor:profile:detail', args=(kwargs['instructor_id'], kwargs['master_syllabus_id'],))})
    elif 'instructor_id' in kwargs:
        return json.dumps({'#profile-container': reverse('editor:profile:detail', args=(kwargs['instructor_id'],))})
    else:
        return json.dumps({'#profile-container': reverse('viewer:search:instructors')})


@register.simple_tag()
def get_json_toc(json_view, json_string):
    try:
        kwargs = json.loads(json_string) if json_string else {}
    except:
        return json.dumps({'error': {'responseText': {'class': 'danger', 'code': 500, 'text': {'format': 'Invalid JSON string. ' + handler_message('bonobo')}, 'type': 'Internal Server Error'}}})
    if json_view == 'admin':
        return json.dumps({'#toc-container': reverse('editor:registration:toc', args=(kwargs['model'],))})
    elif json_view == 'block':
        return json.dumps({'#toc-container': reverse('viewer:block:toc', args=(kwargs['instructor'], kwargs['permalink'],))})
    elif json_view == 'complete' or json_view == 'interactive':
        return json.dumps({'#toc-container': reverse('viewer:interactive:toc', args=(kwargs['section_hash'], json_view))})
    elif json_view == 'curriculum':
        return json.dumps({'#toc-container': reverse('curriculum:toc')})
    elif json_view == 'editor':
        if 'segment_id' in kwargs and int(kwargs['segment_id']) > 0:
            return json.dumps({'#toc-container': reverse('editor:mastersyllabus:toc_segment', args=(kwargs['master_syllabus_id'], kwargs['segment_id'],))})
        else:
            return json.dumps({'#toc-container': reverse('editor:mastersyllabus:toc', args=(kwargs['master_syllabus_id'],))})
    elif json_view == 'internship':
        return json.dumps({'#toc-container': reverse('internship:toc')})
    elif json_view == 'messages':
        if 'message_id' in kwargs and int(kwargs['message_id']) > 0:
            return json.dumps({'#toc-container': reverse('editor:mastersyllabus:toc_message', args=(kwargs['master_syllabus_id'], kwargs['message_id'],))})
        else:
            return json.dumps({'#toc-container': reverse('editor:mastersyllabus:toc', args=(kwargs['master_syllabus_id'],))})
    elif json_view == 'portfolio':
            return json.dumps({'#toc-container': reverse('portfolio:toc')})
    elif json_view == 'traditional':
        return json.dumps({'#toc-container': reverse('viewer:traditional:toc', args=(kwargs['course_code'], kwargs['section_code'], kwargs['term_code']))})
    else:
        return json.dumps({'#toc-container': 'empty'})
