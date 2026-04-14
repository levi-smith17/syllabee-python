from core.views.funcs import get_office_hours as get_off_hours
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from editor.models import SECTION_FORMATS, Section
import re


register = template.Library()


@register.filter(name='addstr')
def addstr(arg1, arg2):
    return str(arg1) + str(arg2)


@register.filter(name='de_slug')
def de_slug(value):
    return str(value).replace('-', '').replace('_', '')


@register.simple_tag()
def define(value=None):
    return value


@register.simple_tag()
def define_if(condition, value_if_true, value_if_false):
    if isinstance(condition, str):
        return value_if_true if eval(condition) else value_if_false
    else:
        return value_if_true if condition else value_if_false


@register.simple_tag()
def define_if_in(operand, sequence, value_if_true, value_if_false):
    return value_if_true if operand in sequence else value_if_false

@register.simple_tag()
def define_elif(value_if_false, *args):
    if len(args) % 2 == 1:
        return value_if_false
    for i in range(0, len(args), 2):
        try:
            if eval(args[i]):
                return args[i + 1]
        except TypeError:
            if args[i]:
                return args[i + 1]
    return value_if_false


@register.simple_tag()
def get_alert_icon(type):
    if type == 'danger':
        return 'x-square'
    elif type == 'info':
        return 'info-square'
    elif type == 'warning':
        return 'exclamation-square'
    else:
        return ''


@register.simple_tag()
def get_id(type, module, component, id=None):
    if id:
        return module + '-' + component + '-' + str(id) + '-' + type
    else:
        return module + '-' + component + '-' + type


@register.simple_tag()
def get_section_from_path(path):
    if '/i/' in path:
        tokens = path.split('/i/')
        try:
            hash_value = tokens[1].strip('/')
            return Section.objects.get(hash=hash_value)
        except Section.DoesNotExist:
            return None
    else:
        return None


@register.simple_tag()
def get_office_hours(instructor):
    return mark_safe(get_off_hours(instructor.user))


@register.filter(name='filter_key')
def filter_key(key):
    if key.startswith('format-'):
        return 'Format'
    else:
        key = key.split('__icontains')
        return key[0].replace('__', ' ').replace('_', ' ').title()


@register.filter(name='filter_value')
def filter_value(key, value):
    if key.startswith('format-'):
        for format in SECTION_FORMATS:
            if format[0] == value:
                return format[1]
    return value


@register.filter(name='format_phone')
def format_phone(phone):
    return phone.replace(' ', '').replace('(', '').replace(')', '').replace('.', '').replace('-', '')


@register.simple_tag()
def has_attr(obj, attr):
    return hasattr(obj, attr)


@register.filter(name='has_group')
def has_group(user, group_name):
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()


@register.simple_tag()
def has_perm(*args):
    for arg in args:
        if not bool(arg):
            return False
    return True


@register.simple_tag()
def has_perm_or(*args):
    for arg in args:
        if arg:
            return True
    return False


@register.simple_tag()
def has_perm_nor(*args):
    for arg in args:
        if arg:
            return False
    return True


@register.simple_tag()
def not_in_list(*args):
    if len(args) % 1:
        return True
    for i in range(0, len(args), 2):
        if args[i] in args[i+1]:
            return False  # Arg is the list.
    return True


@register.filter(name='lower_snake')
def lower_snake(value):
    return str(re.sub(r'[^\w]', '_', value.replace(' ', '_'))).lower().replace('___', '_').replace('__', '_')


@register.filter(name='mapify')
def mapify(value):
    if value:
        return value.replace(' ', '+')
    else:
        return ''


@register.filter(name='negate')
def negate(value):
    return not bool(value)


@register.filter(name='plural')
def plural(value):
    if value:
        if type(value) == int or type(value) == float:
            if value != 1 and value != 1.0:
                return 's'
        else:
            if len(value) != 1:
                return 's'
    else:
        return 's'
    return ''


@register.simple_tag()
def replace(string, old_value, new_value):
    return string.replace(old_value, new_value)


@register.filter(name='stringify')
def stringify(query_set):
    return ", ".join(str(group.name) for group in query_set)


@register.filter
@stringfilter
def template_exists(value):
    try:
        template.loader.get_template(value)
        return True
    except template.TemplateDoesNotExist:
        return False


@register.filter(name='title')
def title(value):
    return str(value).replace('-', ' ').replace('_', ' ').title()


@register.filter(name='upper')
def upper(value):
    return str(value).replace('-', ' ').replace('_', ' ').upper()


@register.filter(name='zfill')
def zfill(value, length):
    return str(value).zfill(length)
