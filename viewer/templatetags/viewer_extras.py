from ..models import *
from ..views.funcs import get_syllabus_title
from django import template
from django.utils.html import mark_safe
from editor.views import render_details, render_grade_determination, render_list, render_schedule, render_table
from editor.models import *
from random import shuffle


register = template.Library()


@register.filter(name='before_today')
def before_today(date_to_compare):
    return date_to_compare < datetime.date.today()


@register.simple_tag
def date_difference(start_time, end_time):
    time = end_time - start_time
    hours, remainder = divmod(time.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if time.days > 0:
        unit = str(time.days) + ' day' + ('' if time.days == 1 else 's')
    elif hours > 0:
        unit = str(hours) + ' hour' + ('' if hours == 1 else 's')
    elif minutes > 0:
        unit = str(minutes) + ' minute' + ('' if minutes == 1 else 's')
    else:
        unit = str(seconds) + ' second' + ('' if seconds == 1 else 's')
    return unit


@register.simple_tag
def date_difference_total(start_time, end_time):
    time = end_time - start_time
    hours, remainder = divmod(time.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    unit = ''
    if time.days > 0:
        unit += str(time.days) + ' day' + ('' if time.days == 1 else 's') + '<br>'
    if hours > 0:
        unit += str(hours) + ' hour' + ('' if hours == 1 else 's') + '<br>'
    if minutes > 0:
        unit += str(minutes) + ' minute' + ('' if minutes == 1 else 's') + '<br>'
    if seconds > 0:
        unit += str(seconds) + ' second' + ('' if seconds == 1 else 's')
    return unit


@register.simple_tag
def get_addendum(master_syllabus, block):
    return Addendum.objects.filter(master_syllabus=master_syllabus, new_block=block).first()


@register.simple_tag
def get_block_responses(master_syllabus, question):
    responses = list(MultipleChoiceQuestionResponse.objects.filter(multiple_choice_question=question))
    if master_syllabus.randomize_responses:
        shuffle(responses)
    return responses


@register.simple_tag
def get_bonds(master_bond, section):
    return (Bond.objects
            .filter(Q(segment__id=master_bond.segment.id, block__printableblock__isnull=False))
            .exclude((Q(block__printableblock__fileblock__coursesyllabusblock__course__isnull=False) &
                      ~Q(block__printableblock__fileblock__coursesyllabusblock__course=section.course)) |
                     (Q(block__printableblock__scheduleblock__isnull=False) &
                      ~Q(block__printableblock__scheduleblock__schedule__term_length=section.term.length)))
            .order_by('order'))


@register.simple_tag
def get_bond_progresses(master_bond_progress, section, view):
    if view == 'complete':
        return (BondProgress.objects
                .filter(master_bond_progress=master_bond_progress)
                .exclude(Q(bond__block__type='response') |
                         (Q(bond__block__printableblock__scheduleblock__isnull=False) &
                          ~Q(bond__block__printableblock__scheduleblock__schedule__term_length=section.term.length)))
                .order_by('bond__order'))
    else:
        return (BondProgress.objects
                .filter(master_bond_progress=master_bond_progress)
                .exclude((Q(bond__block__printableblock__scheduleblock__isnull=False) &
                          ~Q(bond__block__printableblock__scheduleblock__schedule__term_length=section.term.length)))
                .order_by('bond__order'))


@register.simple_tag(takes_context=True)
def get_details(context, details_block, render_mode, *args):
    return mark_safe(render_details(context['request'], details_block, render_mode, *args))


@register.simple_tag(takes_context=True)
def get_grade_determination(context, grade_determination_block, render_mode):
    return mark_safe(render_grade_determination(context['request'], grade_determination_block, render_mode))


@register.simple_tag(takes_context=True)
def get_list(context, list_block, render_mode, *args):
    return mark_safe(render_list(context['request'], list_block, render_mode, *args))


@register.simple_tag(takes_context=True)
def get_schedule(context, schedule, term, render_mode, **kwargs):
    return mark_safe(render_schedule(context['request'], schedule, term, render_mode, **kwargs))


@register.simple_tag()
def get_segment_id_from_section(section):
    segment = Segment.objects.filter(masterbond__masterbondsection__section=section).first()
    return segment.id if segment else -1


@register.simple_tag()
def get_syll_title(section):
    return get_syllabus_title(section)


@register.simple_tag(takes_context=True)
def get_table(context, table, render_mode, *args):
    return mark_safe(render_table(context['request'], table, render_mode, *args))
