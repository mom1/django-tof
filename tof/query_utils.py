# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-30 14:19:55
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-22 20:35:35
from django.utils.translation import get_language

from .settings import DEFAULT_LANGUAGE, FALLBACK_LANGUAGES, SITE_ID


class TranslatableText:
    def __init__(self, instance, attr, *args, **kwargs):
        self._origin = instance._origin_tof.get(attr) or ''
        super().__init__(*args, **kwargs)

    def __getattr__(self, name):
        if name in ('resolve_expression', 'prepare_database_save'):
            raise AttributeError(name)
        attrs = vars(self)
        for val_lang in self.get_fallback_languages(name):
            val = attrs.get(val_lang)
            if val:
                return val
        return attrs.get('_origin') or ''

    def __str__(self):
        return getattr(self, self.get_lang(), '')

    def __repr__(self):
        return str(self)

    def __html__(self):
        return str(self)

    @staticmethod
    def get_lang():
        lang, *_ = get_language().partition('-')
        return lang

    def get_fallback_languages(self, attr):
        for fallback in (attr, FALLBACK_LANGUAGES.get(attr), FALLBACK_LANGUAGES.get(SITE_ID), DEFAULT_LANGUAGE):
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
    __slots__ = ('attname', 'ct', 'field_id')

    def __init__(self, obj_field):
        self.attname = obj_field.name
        self.field_id = obj_field.id
        self.ct = obj_field.content_type.pk

    def __get__(self, instance):
        return instance._all_translations.get(self.attname) or instance._origin_tof.get(self.attname)

    def __set__(self, instance, value):
        if getattr(instance, '_end_init', False):
            attr = self.attname
            trans_text = instance._all_translations.setdefault(attr, TranslatableText(instance, attr))
            setattr(trans_text, trans_text.get_lang(), str(value))
        else:
            instance._origin_tof[self.attname] = value

    def __delete__(self, instance):
        del instance._all_translations[self.attname]  # pragma: no cover
        del type(instance)._meta._field_tof[self.attname]  # pragma: no cover

    def save(self, instance):
        val = instance._all_translations.get(self.attname)
        if val:
            translation, _ = instance._translations.get_or_create(
                content_type_id=self.ct,
                field_id=self.field_id,
                lang_id=val.get_lang(),
            )
            translation.value = val
            translation.save()
