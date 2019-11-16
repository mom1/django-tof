# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-30 14:19:55
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-15 16:17:14
from functools import lru_cache

from django.utils.translation import get_language

from .settings import DEFAULT_LANGUAGE, FALLBACK_LANGUAGES, SITE_ID


class TranslatableText:
    def __init__(self, instance, attr, *args, **kwargs):
        self.instance = instance
        self._origin = instance._origin_tof.get(attr, '')
        super().__init__(*args, **kwargs)

    def __getattr__(self, name):
        if name in ('resolve_expression', 'as_sql'):  # FIXME hasattr catch AttributeError
            raise AttributeError
        for val_lang in self.get_fallback_languages(name):
            if val_lang in vars(self):
                return vars(self).get(val_lang)
        return self._origin

    def __str__(self):
        return getattr(self, self.get_lang(), '')

    def __repr__(self):
        return self.__str__()

    def __html__(self):
        return self.__str__()

    def get_lang(self):
        lang, *_ = get_language().partition('-')
        return lang

    @lru_cache(maxsize=32)
    def get_fallback_languages(self, lang):
        def_val = (DEFAULT_LANGUAGE, )
        fallback_languages = FALLBACK_LANGUAGES.get(
            lang,
            FALLBACK_LANGUAGES.get(
                SITE_ID,
                def_val,
            ),
        ) or def_val

        if not isinstance(fallback_languages, (list, tuple)):
            fallback_languages = (fallback_languages, )
        return (lang, ) + tuple(fl for fl in fallback_languages if fl != lang) + def_val


class DeferredTranslatedAttribute:
    """Получит значение перевода поля для инстанса.

        Args:
            field: Поле модели
    """
    __slots__ = ('field', )

    def __init__(self, field):
        self.field = field

    def __get__(self, instance):
        if instance is None:
            return self

        if not getattr(instance, '_end_init', False):
            return

        return instance._all_translations.get(self.get_field_name()) or instance._origin_tof.get(self.get_field_name())

    def __set__(self, instance, value):
        if getattr(instance, '_end_init', False):
            attr = self.get_field_name()
            trans_text = instance._all_translations.setdefault(attr, TranslatableText(instance, attr))
            setattr(trans_text, self.get_lang(), str(value))
        else:
            instance._origin_tof[self.get_field_name()] = value

    def __delete__(self, instance):
        del instance._all_translations[self.get_field_name()]
        del instance._field_tof[self.get_field_name()]

    def get_lang(self):
        lang, *_ = get_language().partition('-')
        return lang

    def get_field_name(self, ct=None):
        return self.field.attname

    def get_param(self, instance):
        from .models import Language, TranslatableFields
        opts = instance._meta.concrete_model._meta
        fld_obj = TranslatableFields.objects.filter(
            name=self.get_field_name(),
            content_type__app_label=opts.app_label,
            content_type__model=opts.object_name.lower(),
        ).first()
        return {
            'field': fld_obj,
            'lang': Language.objects.filter(iso=self.get_lang()).first(),
        }

    def save(self, instance):
        val = instance._all_translations.get(self.get_field_name())
        if val:
            str_val = str(val)
            translation, _ = instance._translations.get_or_create(**self.get_param(instance))
            translation.value = str_val
            translation.save()
