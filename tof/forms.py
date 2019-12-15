# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-11-09 13:47:17
# @Last Modified by:   MaxST
# @Last Modified time: 2019-12-15 14:13:23
from functools import wraps
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.utils.translation import get_language

from .utils import TranslatableText


class TranslationsForm(forms.ModelForm):
    class Media:
        js = ('tof/js/translation_form.js', )


class TranslationsInLineForm(forms.ModelForm):
    def __init__(self, *args, parent_object=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_object = parent_object
        field = self.fields.get('field')
        if field:
            field.widget.widget.get_url = self.filter_ct(field.widget.widget.get_url)
            field.widget.can_add_related = field.widget.can_change_related = False

    def filter_ct(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            if self.parent_object:
                return f'{response}?ct={ContentType.objects.get_for_model(self.parent_object).pk}'
            return response

        return wrapper


class TranslatableFieldForm(forms.ModelForm):
    class Media:
        js = ('tof/js/translatable_fields_form.js', )


class TranslatableFieldWidget(forms.MultiWidget):
    template_name = 'tof/multiwidget.html'
    input_type = 'text'

    def __init__(self, widget=None, attrs=None):
        widget = widget or forms.TextInput(attrs={**(attrs or {}), 'lang': get_language()})
        super().__init__((widget, ))

    def get_context(self, name, value, attrs):
        context = super(forms.MultiWidget, self).get_context(name, value, attrs)
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized
        # value is a list of values, each corresponding to a widget
        # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)

        final_attrs = context['widget']['attrs']
        input_type = final_attrs.pop('type', self.input_type)
        id_ = final_attrs.get('id')
        subwidgets = []
        for i, widget in enumerate(self.widgets):
            if input_type is not None:
                widget.input_type = input_type
            try:
                widget_lang, widget_value = value[i]
            except IndexError:
                widget_value = None
                widget_lang = None
            if id_:
                widget_attrs = final_attrs.copy()
                widget_attrs['id'] = f'{id_}{widget_lang and f"_{widget_lang}" or ""}'
            else:
                widget_attrs = final_attrs
            widget_name = f'{name}{widget_lang and f"_{widget_lang}"  or ""}'
            subwidgets.append(widget.get_context(widget_name, widget_value, widget_attrs)['widget'])
        context['widget']['subwidgets'] = subwidgets
        return context

    def decompress(self, value):
        if value and isinstance(value, TranslatableText):
            response = [(k, v) for k, v in vars(value).items() if k != '_origin']
            return response or [(get_language(), value._origin)]
        return [(get_language(), value)]

    def render(self, name, value, attrs=None, renderer=None):
        widget = self.widgets.pop(0)
        if isinstance(value, TranslatableText):
            attrs_custom = {**widget.attrs, **(attrs or {})}
            for key in vars(value).keys():
                if key != '_origin':
                    attrs_custom['lang'] = key
                    self.widgets.append(type(widget)(attrs=attrs_custom))
        if not self.widgets:
            self.widgets.append(widget)
        return super().render(name, value, attrs, renderer)

    def value_from_datadict(self, data, files, name):
        response = getattr(self, '_datadict', self)
        if response is self:
            response = []
            chunk_name = f'{name}_'
            for key, val in data.items():
                if key.startswith(chunk_name):
                    *_, lang = key.rpartition('_')
                    response.append((lang, val))
            self._datadict = response
        return response

    def value_omitted_from_data(self, data, files, name):
        return bool(self.value_from_datadict(data, files, name))

    @property
    def media(self):
        css = {'all': ('tof/css/style.css', )}
        js = ('tof/js/translatable_fields_widget.js', )
        return forms.Media(css=css, js=js)


class TranslatableFieldHiddenWidget(TranslatableFieldWidget):
    def __init__(self, attrs=None):
        super().__init__(attrs)
        for widget in self.widgets:
            widget.input_type = 'hidden'


class TranslationFieldModelForm(forms.ModelForm):
    only_current_lang = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _field_tof = getattr(self._meta.model._meta, '_field_tof', {}).get('by_name')
        if _field_tof:
            from .fields import TranslatableFieldFormField
            for name in set(_field_tof.keys()) - set(self.only_current_lang):
                if name in self.fields:
                    self.fields[name] = TranslatableFieldFormField(self.fields[name])
