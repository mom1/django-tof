# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-23 17:24:33
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-01 16:33:57
from django.contrib.contenttypes.fields import (
    GenericForeignKey, GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _


class TranslationsManager(models.Manager):
    """Понадобится для програмного создания переводов."""
    pass


class Translations(models.Model):
    class Meta:
        verbose_name = _('Translation')
        verbose_name_plural = _('Translations')
        ordering = ('sort', )
        unique_together = ('content_type', 'object_id', 'field', 'lang')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    field = models.ForeignKey('TranslatableFields', related_name='translations', on_delete=models.CASCADE)
    lang = models.ForeignKey('Language', related_name='translations', on_delete=models.CASCADE)

    value = models.TextField(_('Value'), help_text=_('Value field'))

    sort = models.IntegerField(_('Sort'), default=0, blank=True, null=True)

    def __str__(self):
        """Пока нужно для отладки.

        Потом можно обьявить для других задач, например показывать перевод текущего языка.

        Returns:
            str
        """
        return f'Translations(content_object={self.content_object}, name={self.field.name}, value={self.value})'


class TranslationsFieldsMixin(models.Model):
    class Meta:
        abstract = True

    _field_tof = {}
    _translations = GenericRelation(Translations, verbose_name=_('Translations'))

    def __getattribute__(self, attr):
        val = self._field_tof.get(attr) if not attr.startswith('_') else None
        if val:
            return val.__get__(self)
        return super().__getattribute__(attr)


class TranslatableFields(models.Model):
    class Meta:
        verbose_name = _('Translatable field')
        verbose_name_plural = _('Translatable fields')
        ordering = ('content_type', 'name')
        unique_together = ('content_type', 'name')

    name = models.CharField(_('Field name'), max_length=250, help_text=_('Name field'))
    title = models.CharField(_('User field name'), max_length=250, help_text=_("Name user's field"))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.content_type.model}|{self.title}'


class Language(models.Model):
    class Meta:
        verbose_name = _('Language')
        verbose_name_plural = _('Languages')
        ordering = ['iso_639_1']

    iso_639_1 = models.CharField(max_length=2, unique=True)
    iso_639_2T = models.CharField(max_length=3, unique=True, blank=True)  # noqa
    iso_639_2B = models.CharField(max_length=3, unique=True, blank=True)  # noqa
    iso_639_3 = models.CharField(max_length=3, blank=True)
    family = models.CharField(max_length=50)

    def __str__(self):
        return self.iso

    @property
    def iso(self):
        return self.iso_639_1
