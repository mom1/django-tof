# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-30 14:19:55
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-01 17:25:46
from itertools import chain

from django.conf import settings
# from django.db.models import Case, IntegerField, Value, When
from django.db.models.query_utils import DeferredAttribute
from django.utils.translation import get_language

from .settings import FALLBACK_LANGUAGES


class DeferredTranslatedAttribute(DeferredAttribute):
    def __get__(self, instance, cls=None):
        """Retrieve and caches the value from the datastore on the first lookup.

        Args:
            instance: current instance
            cls: base class

        Returns:
            the cached value.
        """
        if instance is None:
            return self

        lang = get_language().split('-')[0]
        data = instance.__dict__
        field_name = self.field.attname
        trans_field_name = f'{field_name}_{lang}'
        if data.get(trans_field_name, self) is self:
            # v1
            # val = Translations.objects.get_translation(content_object=instance, field__name=field_name, lang__iso_639_1=lang)
            # v2
            # for val in Translations.objects.filter(content_object=instance, field__name=field_name, lang__iso_639_1=lang).values_list('value', flat=True):
            #     break
            # v3
            # val = instance.__translations.filter(field__name=field_name, lang__iso_639_1=lang).values_list('value', flat=True)
            val = self.get_translation(instance=instance, field_name=field_name, lang=lang)
            # Let's see if the field is part of the parent chain. If so we
            # might be able to reuse the already loaded value. Refs #18343.
            if val is None:
                val = self._check_parent_chain(instance)
                if val is None:
                    instance.refresh_from_db(fields=[field_name])
                    val = getattr(instance, field_name)
            data[trans_field_name] = val
        return data[trans_field_name]

    def get_translation(self, instance=None, field_name=None, lang=None):
        fallback_languages = self.get_fallback_languages(lang)

        for val_lang in chain((lang, ), fallback_languages):
            translations = instance._all_translations.get(f'{field_name}_{val_lang}')
            if translations:
                return translations

    def get_fallback_languages(self, lang):
        if not hasattr(self, '_fallback_languages'):
            fallback_languages = getattr(settings, 'FALLBACK_LANGUAGES', FALLBACK_LANGUAGES)
            site_id = getattr(settings, 'SITE_ID', None)
            fallback_languages = fallback_languages.get(
                lang,
                fallback_languages.get(
                    site_id,
                    ('en', ),
                ),
            )
            if not fallback_languages:
                fallback_languages = ('en', )
            elif not isinstance(fallback_languages, (list, tuple)):
                fallback_languages = (fallback_languages, )
            self._fallback_languages = fallback_languages
        return self._fallback_languages
