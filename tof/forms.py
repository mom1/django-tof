# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-11-09 13:47:17
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-27 13:08:19
from django import forms

from .utils import TranslatableText


class TranslationsForm(forms.ModelForm):
    class Media:
        js = ('tof/js/translation_form.js', )


class TranslatableFieldForm(forms.ModelForm):
    class Media:
        js = ('tof/js/translatable_fields_form.js', )


class TranslatableFieldWidget(forms.MultiWidget):
    template_name = 'tof/multiwidget.html'

    def __init__(self, attrs=None):
        self.def_lang = ''
        super().__init__((forms.TextInput(attrs=attrs), ))

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized
        # value is a list of values, each corresponding to a widget
        # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)

        final_attrs = context['widget']['attrs']
        input_type = final_attrs.pop('type', None)
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
                widget_attrs['id'] = f'{id_}_{i}{widget_lang and f"_{widget_lang}" or ""}'
            else:
                widget_attrs = final_attrs
            widget_name = f'{name}_{i}{widget_lang and f"_{widget_lang}"  or ""}'
            subwidgets.append(widget.get_context(widget_name, widget_value, widget_attrs)['widget'])
        context['widget']['subwidgets'] = subwidgets
        return context

    def decompress(self, value):
        if value and isinstance(value, TranslatableText):
            return [(k, v) for k, v in vars(value).items() if k != '_origin']
        return [(None, value)]

    def render(self, name, value, attrs=None, renderer=None):
        if isinstance(value, TranslatableText):
            widget = self.widgets.pop(0)
            attrs_custom = {**widget.attrs, **(attrs or {})}
            for key in vars(value).keys():
                if key != '_origin':
                    if not self.widgets:
                        self.def_lang = key
                    attrs_custom['lang'] = key
                    self.widgets.append(forms.TextInput(attrs=attrs_custom))
        return super().render(name, value, attrs, renderer)

    def value_from_datadict(self, data, files, name):
        i, response = 0, []
        for key, val in data.items():
            chunk_name = f'{name}_{i}'
            if key == chunk_name:
                response.append((None, val))
                i += 1
            elif key.startswith(chunk_name):
                *_, lang = key.rpartition('_')
                response.append((lang, val))
                i += 1
        return response

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
