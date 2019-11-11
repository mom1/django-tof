# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-23 17:24:33
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-11 12:16:32
from django.contrib.contenttypes.fields import (
    GenericForeignKey, GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _


class TranslationsManager(models.Manager):
    """Понадобится для програмного создания переводов."""
    pass


class Translations(models.Model):
    class Meta:
        verbose_name = _('Translation')
        verbose_name_plural = _('Translations')
        unique_together = ('content_type', 'object_id', 'field', 'lang')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(help_text=_('First set the field'))
    content_object = GenericForeignKey()

    field = models.ForeignKey('TranslatableFields', related_name='translations', on_delete=models.CASCADE)
    lang = models.ForeignKey('Language', related_name='translations', on_delete=models.CASCADE)

    value = models.TextField(_('Value'), help_text=_('Value field'))

    def __str__(self):
        """Пока нужно для отладки.

        Потом можно обьявить для других задач, например показывать перевод текущего языка.

        Returns:
            str
        """
        return f'{self.content_object}: lang={self.lang}, field={self.field.name}, value={self.value})'


class TranslationsFieldsMixin(models.Model):
    class Meta:
        abstract = True

    _field_tof = {}
    _end_init = False
    _translations = GenericRelation(Translations, verbose_name=_('Translations'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._end_init = True

    def __getattribute__(self, attr):
        val = self._field_tof.get(attr) if not attr.startswith('_') and self._end_init else None
        if val:
            return val.get(self) or super().__getattribute__(attr)
        return super().__getattribute__(attr)

    def __setattr__(self, name, value):
        val = self._field_tof.get(name) if self._end_init else None
        if val:
            return val.set_val(self, value)
        super().__setattr__(name, value)

    @cached_property
    def _all_translations(self, **kwargs):
        translations = self._translations.all()
        for name, lang, val in translations.values_list('field__name', 'lang__iso_639_1', 'value'):
            field_name = f'{name}_{lang}'
            kwargs[field_name] = val
            setattr(self, field_name, val)
        return kwargs

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for def_trans_attrs in self._field_tof.values():
            def_trans_attrs.save(self)

    @classmethod
    def _add_deferred_translated_field(cls, name):
        from .query_utils import DeferredTranslatedAttribute
        cls._field_tof[name] = DeferredTranslatedAttribute(getattr(getattr(cls, name), 'field', None))

    @classmethod
    def _del_deferred_translated_field(cls, name):
        try:
            del cls._field_tof[name]
        except Exception:
            pass


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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        cls = self.content_type.model_class()
        if not issubclass(cls, TranslationsFieldsMixin):
            cls.__bases__ = (TranslationsFieldsMixin, ) + cls.__bases__
        cls._add_deferred_translated_field(self.name)

    def delete(self, *args, **kwargs):
        cls = self.content_type.model_class()
        name = self.name
        super().delete(*args, **kwargs)
        cls._del_deferred_translated_field(name)


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
