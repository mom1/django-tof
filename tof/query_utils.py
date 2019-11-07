# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-30 14:19:55
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-07 09:55:39
from itertools import chain

from django.utils.translation import get_language

from .settings import DEFAULT_LANGUAGE, FALLBACK_LANGUAGES, SITE_ID


class DeferredTranslatedAttribute:
    def __init__(self, field):
        self.field = field

    def get(self, instance):
        """Retrieve and caches the value from the datastore on the first lookup.

        Args:
            instance: current instance

        Returns:
            the cached value.
        """
        if instance is None:
            return self
        lang = get_language().split('-')[0]
        data = instance.__dict__
        field_name = self.field.attname
        trans_field_name = f'{field_name}_{lang}'
        val = data.get(trans_field_name)
        if not val:
            val = data[trans_field_name] = self.get_translation(instance=instance, field_name=field_name, lang=lang)
        return val or data.get(field_name)

    def get_translation(self, instance=None, field_name=None, lang=None):
        fallback_languages = self.get_fallback_languages(lang)

        for val_lang in chain((lang, ), fallback_languages):
            translation = instance._all_translations.get(f'{field_name}_{val_lang}')
            if translation:
                return translation

    def get_fallback_languages(self, lang):
        if not hasattr(self, '_fallback_languages'):
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
            self._fallback_languages = fallback_languages
        return self._fallback_languages
