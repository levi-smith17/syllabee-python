from django import forms
from django.db.models import Q
from django.template import loader
from django.utils.safestring import mark_safe


class DatalistWidget(forms.Widget):
    template_name = 'core/widgets/datalist.html'
    input_type = 'datalist'

    def __init__(self, model, choices=(), filters=Q(), exclude=Q(), values='', order_by=None, attrs=None):
        super().__init__()
        self.model = model
        self.choices = choices
        self.filters = filters
        self.exclude = exclude
        self.values = values
        self.order_by = order_by
        self.extra_attrs = attrs

    def get_context(self, name, value, attrs=None):
        try:
            if value:
                value = self.model.objects.get(pk=int(value))
        except:
            pass
        if self.choices:
            choices = self.choices
        elif self.values:
            choices = (self.model.objects
                       .filter(self.filters)
                       .exclude(self.exclude)
                       .values_list(self.values, flat=True)
                       .order_by(self.order_by if self.order_by else self.values).distinct())
        else:
            choices = self.model.objects.filter(self.filters).exclude(self.exclude)
        all_attrs = self.build_attrs(attrs, self.extra_attrs)
        return {'choices': choices, 'widget': {
            'name': name,
            'value': value,
            'attrs': all_attrs,
        }}

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)


class QuillWidget(forms.Widget):
    template_name = 'core/widgets/quill.html'
    input_type = 'quill'

    def __init__(self, attrs=None):
        super().__init__()
        self.extra_attrs = attrs

    def get_context(self, name, value, attrs=None):
        all_attrs = self.build_attrs(attrs, self.extra_attrs)
        return {'widget': {
            'name': name,
            'value': value,
            'attrs': all_attrs,
        }}

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)
