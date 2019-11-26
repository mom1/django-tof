# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-29 10:05:01
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-22 14:24:05
import sys

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
            for arg in ('migrate', 'makemigrations'):
                if arg in sys.argv:
                    return  # pragma: no cover
            for field in self.models_module.TranslatableField.objects.all():
                field.add_translation_to_class()
