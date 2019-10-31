# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-29 10:05:01
# @Last Modified by:   MaxST
# @Last Modified time: 2019-10-31 19:49:43
from django.apps import AppConfig
from django.db.models.signals import post_init, pre_init

from .query_utils import DeferredTranslatedAttribute


class TofConfig(AppConfig):
    name = 'tof'

    def ready(self):
        from django.contrib.contenttypes.models import ContentType
        from .models import TranslationsFieldsMixin

        prev = None
        for ct, attr in self.get_model('TranslatableFields').objects.values_list('content_type', 'name'):
            # import ipdb; ipdb.set_trace()
            if prev != ct:
                prev = ct
                cls = ContentType.objects.get_for_id(ct).model_class()
                if not issubclass(cls, TranslationsFieldsMixin):
                    cls.__bases__ = (TranslationsFieldsMixin, ) + cls.__bases__
            post_init.connect(self.attach_attrs, sender=DeferredTranslatedAttribute(getattr(getattr(cls, attr), 'field', None)))
            # flds = getattr(cls, '__flds_tof', {})
            # flds[attr] = DeferredTranslatedAttribute(getattr(getattr(cls, attr), 'field', None))
            # setattr(cls, '__flds_tof', flds)
        # print(getattr(cls, '__flds_tof', {}))

    def attach_attrs(self, sender, *args, **kwargs):
        instance = kwargs['instance']
        setattr(instance, sender.field.attname, sender)
