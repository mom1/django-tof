# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-29 10:05:01
# @Last Modified by:   MaxST
# @Last Modified time: 2019-10-30 17:12:16
from django.apps import AppConfig


class TofConfig(AppConfig):
    name = 'tof'

    def ready(self):
        from django.contrib.contenttypes.models import ContentType
        from .models import TranslationsFieldsMixin

        for ct in self.get_model('TranslatableFields').objects.values_list('content_type', flat=True).distinct():
            cls = ContentType.objects.get_for_id(ct).model_class()
            if TranslationsFieldsMixin not in cls.__bases__:
                cls.__bases__ = (TranslationsFieldsMixin, ) + cls.__bases__
