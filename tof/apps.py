# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-29 10:05:01
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-01 16:33:08
from django.apps import AppConfig

from .query_utils import DeferredTranslatedAttribute


class TofConfig(AppConfig):
    name = 'tof'

    def ready(self):
        from django.contrib.contenttypes.models import ContentType
        from .models import TranslationsFieldsMixin

        prev = None
        # Exception if did not make migration
        try:
            translatable_fields = self.get_model('TranslatableFields')
        except Exception:
            return

        for ct, attr in translatable_fields.objects.values_list('content_type', 'name'):
            if prev != ct:
                prev = ct
                cls = ContentType.objects.get_for_id(ct).model_class()
                if not issubclass(cls, TranslationsFieldsMixin):
                    cls.__bases__ = (TranslationsFieldsMixin, ) + cls.__bases__
            fields = cls._field_tof
            fields[attr] = DeferredTranslatedAttribute(getattr(getattr(cls, attr), 'field', None))

    def attach_attrs(self, sender, *args, **kwargs):
        instance = kwargs['instance']
        setattr(instance, sender.field.attname, sender)
