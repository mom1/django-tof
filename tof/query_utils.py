# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-30 14:19:55
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-12 21:54:25
from functools import lru_cache

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import get_language

from .models import Language, TranslatableFields
from .settings import DEFAULT_LANGUAGE, FALLBACK_LANGUAGES, SITE_ID


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

        field_name = self.get_field_name()
        trans_field_name = self.get_trans_field_name()
        data = instance.__dict__
        data[trans_field_name] = data.get(trans_field_name) or self.get_translation(instance=instance, field_name=field_name)
        return data.get(trans_field_name) or data.get(field_name)

    def get_lang(self, is_obj=False):
        lang, *_ = get_language().partition('-')
        return lang if not is_obj else Language.objects.filter(iso_639_1=lang).first()

    def get_field_name(self, ct=None):
        name = self.field.attname
        return name if not ct else TranslatableFields.objects.filter(name=name, content_type=ct).first()

    def get_trans_field_name(self):
        return f'{self.get_field_name()}_{self.get_lang()}'

    def get_translation(self, instance=None, field_name=None, language=None):
        lang = language or self.get_lang()
        fld_name = field_name or self.get_field_name()
        fallback_languages = self.get_fallback_languages(lang)

        for val_lang in fallback_languages:
            translation = instance._all_translations.get(f'{fld_name}_{val_lang}')
            if translation:
                return translation
        return vars(instance).get(f'{self.get_field_name()}_origin')

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

    def __set__(self, instance, value):
        if not getattr(instance, '_end_init', False):
            instance.__dict__[f'{self.get_field_name()}_origin'] = value
            return
        instance.__dict__[self.get_trans_field_name()] = value

    def save(self, instance):
        val = instance.__dict__.get(self.get_trans_field_name())
        if val:
            ct = ContentType.objects.get_for_model(instance, for_concrete_model=False)
            translation, _ = instance._translations.get_or_create(field=self.get_field_name(ct), lang=self.get_lang(True))
            translation.value = val
            translation.save()

    def __delete__(self, instance):
        del instance.__dict__[self.get_field_name()]
        del instance._field_tof[self.get_field_name()]
