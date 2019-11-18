# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-29 10:05:01
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-18 12:54:07
from django.apps import AppConfig
from django.db import connection


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
            from .models import prepare_cls_for_translate, TranslatableField
            from .managers import TranslationManager
            trans_mng = TranslationManager()

            for field in TranslatableField.objects.all():
                cls = field.content_type.model_class()
                prepare_cls_for_translate(cls, field, trans_mng)
