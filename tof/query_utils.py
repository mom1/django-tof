# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-30 14:19:55
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-18 12:14:02
from django.utils.translation import get_language

from .settings import DEFAULT_LANGUAGE, FALLBACK_LANGUAGES, SITE_ID


class TranslatableText:
    def __init__(self, instance, attr, *args, **kwargs):
        self._origin = instance._origin_tof.get(attr, '')
        super().__init__(*args, **kwargs)

    def __getattr__(self, name):
        attrs = vars(self)
        for val_lang in self.get_fallback_languages(name):
            val = attrs.get(val_lang)
            if val:
                return val

    def __str__(self):
        return getattr(self, self.get_lang(), '')

    def __repr__(self):
        return str(self)

    def __html__(self):
        return str(self)

    def resolve_expression(self, *args, **kwargs):
        return str(self)

    @staticmethod
    def get_lang():
        lang, *_ = get_language().partition('-')
        return lang

    def get_fallback_languages(self, attr):
        for fallback in (attr, FALLBACK_LANGUAGES.get(attr), FALLBACK_LANGUAGES.get(SITE_ID), DEFAULT_LANGUAGE, '_origin'):
            if isinstance(fallback, (list, tuple)):
                yield from (lang for lang in fallback if lang != attr)
            else:
                yield fallback


class DeferredTranslatedAttribute:
    """Получит значение перевода поля для инстанса.

        Args:
            model_field: Поле модели
            obj_field: Объект поля. тип TranslatableField
    """
    __slots__ = ('model_field', 'obj_field')

    def __init__(self, field, obj_field):
        self.model_field = field
        self.obj_field = obj_field

    def __get__(self, instance):
        return instance._all_translations.get(self.get_field_name()) or instance._origin_tof.get(self.get_field_name())

    def __set__(self, instance, value):
        if getattr(instance, '_end_init', False):
            attr = self.get_field_name()
            trans_text = instance._all_translations.setdefault(attr, TranslatableText(instance, attr))
            setattr(trans_text, trans_text.get_lang(), str(value))
        else:
            instance._origin_tof[self.get_field_name()] = value

    def __delete__(self, instance):
        del instance._all_translations[self.get_field_name()]
        del instance._field_tof[self.get_field_name()]

    def get_field_name(self, ct=None):
        return self.model_field.attname

    def save(self, instance):
        val = instance._all_translations.get(self.get_field_name())
        if val:
            str_val = str(val)
            translation, _ = instance._translations.get_or_create(field=self.obj_field, lang_id=val.get_lang())
            translation.value = str_val
            translation.save()
