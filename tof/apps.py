# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-29 10:05:01
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-07 17:28:26
from django.apps import AppConfig
from django.db import connection
from django.db.models import F


class TofConfig(AppConfig):
    """Класс настроек приложения.

    Тут будем при старте сервера кэшировать список переводимых полей

    Attributes:
        name: Имя приложения
    """
    name = 'tof'

    def ready(self):
        from django.contrib.contenttypes.models import ContentType
        from .models import TranslationsFieldsMixin

        # Exception if did not make migration
        try:
            if not connection.introspection.table_names():
                return
        except Exception:
            return

        prev = None
        for ct in ContentType.objects.filter(translatablefields__isnull=False).annotate(attr=F('translatablefields__name')):
            if prev != ct:
                prev = ct
                cls = ct.model_class()
                if issubclass(cls, TranslationsFieldsMixin):
                    continue
                cls.__bases__ = (TranslationsFieldsMixin, ) + cls.__bases__
            cls._add_deferred_translated_field(ct.attr)
