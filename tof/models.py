# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-23 17:24:33
# @Last Modified by:   MaxST
# @Last Modified time: 2019-12-02 18:08:48

from django.contrib.contenttypes.fields import (
    GenericForeignKey, GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from .managers import TranslationManager
from .settings import CHANGE_DEFAULT_MANAGER
from .utils import TranslatableText


class Translation(models.Model):
    class Meta:
        verbose_name = _('Translation')
        verbose_name_plural = _('Translation')
        unique_together = ('content_type', 'object_id', 'field', 'lang')

    content_type = models.ForeignKey(
        ContentType,
        limit_choices_to=~Q(app_label='tof'),
        on_delete=models.CASCADE,
        related_name='translations',
    )
    object_id = models.PositiveIntegerField(help_text=_('First set the field'))
    content_object = GenericForeignKey()

    field = models.ForeignKey('TranslatableField', related_name='translations', on_delete=models.CASCADE)
    lang = models.ForeignKey(
        'Language',
        related_name='translations',
        limit_choices_to=Q(is_active=True),
        on_delete=models.CASCADE,
    )

    value = models.TextField(_('Value'), help_text=_('Value field'))

    def __str__(self):
        return f'{self.content_object}.{self.field.name}.{self.lang} = "{self.value}"'


class TranslationFieldMixin(models.Model):
    class Meta:
        abstract = True

    _translations = GenericRelation(Translation, verbose_name=_('Translation'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._end_init = True

    @cached_property
    def _all_translations(self):
        attrs, names_mapper = vars(self), self._meta._field_tof['by_id']
        for trans in self._translations.all():
            name = names_mapper[trans.field_id].name
            attrs[name] = trans_obj = attrs.get(name) or TranslatableText()
            vars(trans_obj)[trans.lang_id] = trans.value
        return attrs

    def get_translation(self, name):
        attrs = vars(self)
        if '_end_init' in attrs:
            attrs = self._all_translations
        return attrs.get(name) or TranslatableText()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for translated_field in self._meta._field_tof['by_id'].values():
            translated_field.save_translation(self)


class TranslatableField(models.Model):
    class Meta:
        verbose_name = _('Translatable field')
        verbose_name_plural = _('Translatable fields')
        ordering = ('content_type', 'name')
        unique_together = ('content_type', 'name')

    name = models.CharField(_('Field name'), max_length=250, help_text=_('Name field'))
    title = models.CharField(_('User field name'), max_length=250, help_text=_("Name user's field"))
    content_type = models.ForeignKey(
        ContentType,
        limit_choices_to=~Q(app_label='tof'),
        on_delete=models.CASCADE,
        related_name='translatablefields',
    )

    def __str__(self):
        return f'{self.content_type.model}|{self.title}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.add_translation_to_class()

    def delete(self, *args, **kwargs):
        self.remove_translation_from_class()
        super().delete(*args, **kwargs)

    def __get__(self, instance, instance_cls):
        return instance.get_translation(self.name) if instance else vars(instance_cls).get(self.name)

    def __set__(self, instance, value):
        attrs = vars(instance)
        if isinstance(value, TranslatableText):
            attrs[self.name] = value
        else:
            translation = attrs[self.name] = instance.get_translation(self.name)
            vars(translation)[translation.get_lang() if '_end_init' in attrs else '_origin'] = str(value)

    def __delete__(self, instance):
        vars(self).pop(self.name, None)
        instance._meta._field_tof['by_name'].pop(instance._meta._field_tof['by_id'].pop(self.id, self).name, None)

    def save_translation(self, instance):
        val = instance.get_translation(self.name)
        if val:
            for lang, value in vars(val).items():
                if lang != '_origin':
                    translation, _ = instance._translations.get_or_create(field=self, lang_id=lang)
                    translation.value = value
                    translation.save()

    def add_translation_to_class(self, trans_mng=None):
        cls = self.content_type.model_class()
        if not hasattr(cls._meta, '_field_tof'):
            cls.__bases__ = (TranslationFieldMixin, ) + cls.__bases__
            cls._meta._field_tof = {'by_name': {}, 'by_id': {}}
            if CHANGE_DEFAULT_MANAGER and not isinstance(cls._default_manager, TranslationManager):
                origin = cls.objects
                new_mng_cls = type(f'TranslationManager{cls.__name__}', (TranslationManager, type(origin)), {})
                trans_mng = trans_mng or new_mng_cls()
                trans_mng.contribute_to_class(cls, trans_mng.default_name)
                cls._meta.default_manager_name = trans_mng.default_name
                # FIXME
                del cls.objects
                trans_mng.contribute_to_class(cls, 'objects')
                origin.contribute_to_class(cls, 'objects_origin')
        setattr(
            cls,
            cls._meta._field_tof['by_name'].setdefault(cls._meta._field_tof['by_id'].setdefault(self.id, self).name, self).name,
            self,
        )

    def remove_translation_from_class(self):
        cls = self.content_type.model_class()
        cls._meta._field_tof['by_name'].pop(cls._meta._field_tof['by_id'].pop(self.id, self).name, None)
        delattr(cls, self.name)
        field = cls._meta.get_field(self.name)
        field.contribute_to_class(cls, self.name)
        if not cls._meta._field_tof['by_id']:
            del cls._meta._field_tof
            cls.__bases__ = tuple(base for base in cls.__bases__ if base != TranslationFieldMixin)  # important!
            if CHANGE_DEFAULT_MANAGER and isinstance(cls._default_manager, TranslationManager):
                delattr(cls, cls._default_manager.default_name)
                cls._meta.default_manager_name = None
                mng = cls.objects_origin
                del cls.objects
                del cls.objects_origin
                mng.contribute_to_class(cls, 'objects')


class Language(models.Model):
    class Meta:
        verbose_name = _('Language')
        verbose_name_plural = _('Languages')
        ordering = ['iso']

    iso = models.CharField(max_length=2, unique=True, primary_key=True)
    is_active = models.BooleanField(_(u'Active'), default=True)

    def __str__(self):
        return self.iso
