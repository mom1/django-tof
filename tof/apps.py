# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-29 10:05:01
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-17 15:33:07
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
            from .models import prepare_cls_for_translate
            from .managers import TranslationsManager
            trans_mng = TranslationsManager()
            for ct in ContentType.objects.filter(translatablefields__isnull=False).annotate(attr=F('translatablefields__name')):
                cls = ct.model_class()
                prepare_cls_for_translate(cls, ct.attr, trans_mng)
