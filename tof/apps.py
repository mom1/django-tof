# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-29 10:05:01
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-14 15:46:30
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
        # Exception if did not make migration
        if connection.introspection.table_names():
            from django.contrib.contenttypes.models import ContentType
            from .models import TranslationsFieldsMixin, tof_filter, TranslationsManager
            trans_mng = TranslationsManager()
            for ct in ContentType.objects.filter(translatablefields__isnull=False).annotate(attr=F('translatablefields__name')):
                cls = ct.model_class()
                if not issubclass(cls, TranslationsFieldsMixin):
                    cls.__bases__ = (TranslationsFieldsMixin, ) + cls.__bases__
                    trans_mng.contribute_to_class(cls, 'trans_objects')
                    for attr in ('filter', 'exclude', 'get'):
                        setattr(cls.objects, attr, tof_filter(getattr(cls.objects, attr)))
                        setattr(cls.objects._queryset_class, attr, tof_filter(getattr(cls.objects._queryset_class, attr)))
                cls._add_deferred_translated_field(ct.attr)
