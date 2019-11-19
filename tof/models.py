# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-23 17:24:33
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-19 15:27:21

from django.contrib.contenttypes.fields import (
    GenericForeignKey, GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from .managers import TranslationManager
from .query_utils import DeferredTranslatedAttribute, TranslatableText
from .settings import CHANGE_DEFAULT_MANAGER


class Translation(models.Model):
    class Meta:
        verbose_name = _('Translation')
        verbose_name_plural = _('Translation')
        unique_together = ('content_type', 'object_id', 'field', 'lang')

    content_type = models.ForeignKey(ContentType, limit_choices_to=~Q(app_label='tof'), on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(help_text=_('First set the field'))
    content_object = GenericForeignKey()

    field = models.ForeignKey('TranslatableField', related_name='Translation', on_delete=models.CASCADE)
    lang = models.ForeignKey(
        'Language',
        related_name='Translation',
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
        self._origin_tof = {}
        self._end_init = False
        super().__init__(*args, **kwargs)
        self._end_init = True

    @cached_property
    def _all_translations(self, **kwargs):
        for trans in self._translations.all():
            name = trans.field.name
            trans_obj = kwargs.setdefault(name, TranslatableText(self, name))
            setattr(trans_obj, trans.lang_id, trans.value)
        return kwargs

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for def_trans_attrs in type(self)._meta._field_tof.values():
            def_trans_attrs.save(self)

    @classmethod
    def _add_deferred_translated_field(cls, field):
        translator = cls._meta._field_tof[field.name] = DeferredTranslatedAttribute(cls._meta.get_field(field.name), field)
        setattr(cls, field.name,
                property(
                    fget=translator.__get__,
                    fset=translator.__set__,
                    fdel=translator.__delete__,
                    doc=repr(translator),
                ))

    @classmethod
    def _del_deferred_translated_field(cls, name):
        try:
            fld = cls._meta._field_tof[name].model_field
            del cls._meta._field_tof[name]
            delattr(cls, name)
            fld.contribute_to_class(cls, name)
        except Exception:
            pass


class TranslatableField(models.Model):
    class Meta:
        verbose_name = _('Translatable field')
        verbose_name_plural = _('Translatable fields')
        ordering = ('content_type', 'name')
        unique_together = ('content_type', 'name')

    name = models.CharField(_('Field name'), max_length=250, help_text=_('Name field'))
    title = models.CharField(_('User field name'), max_length=250, help_text=_("Name user's field"))
    content_type = models.ForeignKey(ContentType, limit_choices_to=~Q(app_label='tof'), on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.content_type.model}|{self.title}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        prepare_cls_for_translate(self.content_type.model_class(), self)

    def delete(self, *args, **kwargs):
        cls = self.content_type.model_class()
        ct_pk = self.content_type.pk
        name = self.name
        super().delete(*args, **kwargs)

        restore_cls_after_translate(
            cls,
            name,
            ContentType.objects.filter(translatablefield__isnull=False, id=ct_pk).exists(),
        )


class Language(models.Model):
    class Meta:
        verbose_name = _('Language')
        verbose_name_plural = _('Languages')
        ordering = ['iso']

    iso = models.CharField(max_length=2, unique=True, primary_key=True)
    is_active = models.BooleanField(_(u'Active'), default=True)

    def __str__(self):
        return self.iso


def prepare_cls_for_translate(cls, obj_field, trans_mng=None):
    if not issubclass(cls, TranslationFieldMixin):
        cls.__bases__ = (TranslationFieldMixin, ) + cls.__bases__
        cls._meta._field_tof = {}
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
    cls._add_deferred_translated_field(obj_field)


def restore_cls_after_translate(cls, attr, keep_mixin):
    cls._del_deferred_translated_field(attr)
    del cls._meta._field_tof
    if issubclass(cls, TranslationFieldMixin) and not keep_mixin:
        cls.__bases__ = cls.__bases__[1:]
        if CHANGE_DEFAULT_MANAGER and isinstance(cls._default_manager, TranslationManager):
            delattr(cls, cls._default_manager.default_name)
            cls._meta.default_manager_name = None
            mng = cls.objects_origin
            del cls.objects
            del cls.objects_origin
            mng.contribute_to_class(cls, 'objects')
