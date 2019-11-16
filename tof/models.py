# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-23 17:24:33
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-16 19:55:24
from functools import wraps

from django.contrib.contenttypes.fields import (
    GenericForeignKey, GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property
from django.utils.translation import get_language, gettext_lazy as _

from .query_utils import DeferredTranslatedAttribute, TranslatableText
from .settings import (
    CHANGE_DEFAULT_MANAGER, DEFAULT_FILTER_LANGUAGE, DEFAULT_LANGUAGE,
)


def tof_prefetch(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        query_set = func(*args, **kwargs)
        return query_set.prefetch_related('_translations__field', '_translations__lang')

    return wrapper


def tof_filter(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        new_args, new_kwargs = args, kwargs
        if issubclass(self.model, TranslationsFieldsMixin):
            new_args = []
            for arg in args:
                if isinstance(arg, Q):
                    # modify Q objects (warning: recursion ahead)
                    arg = expand_q_filters(arg, self.model)
                new_args.append(arg)

            new_kwargs = {}
            for key, value in list(kwargs.items()):
                # modify kwargs (warning: recursion ahead)
                new_key, new_value, repl = expand_filter(self.model, key, value)
                new_kwargs.update({new_key: new_value})

        return func(self, *new_args, **new_kwargs)

    return wrapper


def expand_q_filters(q, root_cls):
    new_children = []
    for qi in q.children:
        if isinstance(qi, tuple):
            # this child is a leaf node: in Q this is a 2-tuple of:
            # (filter parameter, value)
            key, value, repl = expand_filter(root_cls, *qi)
            query = Q(**{key: value})
            if repl:
                query |= Q(**{qi[0]: qi[1]})
            new_children.append(query)
        else:
            # this child is another Q node: recursify!
            new_children.append(expand_q_filters(qi, root_cls))
    q.children = new_children
    return q


def expand_filter(model_cls, key, value):
    field, sep, lookup = key.partition('__')
    if field in model_cls._field_tof:
        ct = ContentType.objects.get_for_model(model_cls)
        query = (Q(field__content_type__id=ct.pk) & Q(field__name=field))  # noqa
        if DEFAULT_FILTER_LANGUAGE == '__all__':
            pass
        elif DEFAULT_FILTER_LANGUAGE == 'current':
            query &= Q(lang=get_language())
        elif isinstance(DEFAULT_FILTER_LANGUAGE, str):
            query &= Q(lang=DEFAULT_FILTER_LANGUAGE)
        elif isinstance(DEFAULT_FILTER_LANGUAGE, (list, tuple)):
            query &= Q(lang__in=DEFAULT_FILTER_LANGUAGE)
        elif isinstance(DEFAULT_FILTER_LANGUAGE, dict):
            query &= Q(lang__in=DEFAULT_FILTER_LANGUAGE.get(get_language(), (DEFAULT_LANGUAGE, )))
        else:
            query &= Q(lang=get_language())
        query &= Q(**{f'value{sep}{lookup}': value})
        new_val = Translations.objects.filter(query).values_list('object_id', flat=True)
        return 'id__in', new_val, True
    return key, value, False


class TranslationsQuerySet(models.QuerySet):
    @tof_filter
    def filter(self, *args, **kwargs):  # noqa
        return super().filter(*args, **kwargs)

    @tof_filter  # noqa
    def exclude(self, *args, **kwargs):
        return super().exclude(*args, **kwargs)

    @tof_filter  # noqa
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)


class TranslationsManager(models.Manager):
    default_name = 'trans_objects'
    _queryset_class = TranslationsQuerySet

    def __init__(self, name=None):
        self.default_name = name or self.default_name
        super().__init__()

    @tof_filter  # noqa
    def filter(self, *args, **kwargs):  # noqa
        return super().filter(*args, **kwargs)

    @tof_filter  # noqa
    def exclude(self, *args, **kwargs):
        return super().exclude(*args, **kwargs)

    @tof_filter  # noqa
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    @tof_prefetch
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs)


class Translations(models.Model):
    class Meta:
        verbose_name = _('Translation')
        verbose_name_plural = _('Translations')
        unique_together = ('content_type', 'object_id', 'field', 'lang')

    content_type = models.ForeignKey(ContentType, limit_choices_to=~Q(app_label='tof'), on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(help_text=_('First set the field'))
    content_object = GenericForeignKey()

    field = models.ForeignKey('TranslatableFields', related_name='translations', on_delete=models.CASCADE)
    lang = models.ForeignKey(
        'Language',
        related_name='translations',
        limit_choices_to=Q(is_active=True),
        on_delete=models.CASCADE,
    )

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

    _end_init = False
    _field_tof = {}
    _translations = GenericRelation(Translations, verbose_name=_('Translations'))

    def __init__(self, *args, **kwargs):
        self._origin_tof = {}
        super().__init__(*args, **kwargs)
        self._end_init = True

    @cached_property
    def _all_translations(self, **kwargs):
        for trans in self._translations.all():
            name = trans.field.name
            trans_obj = kwargs.setdefault(name, TranslatableText(self, name))
            setattr(trans_obj, trans.lang.pk, trans.value)
        return kwargs

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for def_trans_attrs in self._field_tof.values():
            def_trans_attrs.save(self)

    @classmethod
    def _add_deferred_translated_field(cls, name):
        translator = cls._field_tof[name] = DeferredTranslatedAttribute(cls._meta.get_field(name))
        setattr(
            cls, name,
            property(
                fget=translator.__get__,
                fset=translator.__set__,
                fdel=translator.__delete__,
                doc=translator.__repr__(),
            ))

    @classmethod
    def _del_deferred_translated_field(cls, name):
        try:
            delattr(cls, name)
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
    content_type = models.ForeignKey(ContentType, limit_choices_to=~Q(app_label='tof'), on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.content_type.model}|{self.title}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        prepare_cls_for_translate(self.content_type.model_class(), self.name)

    def delete(self, *args, **kwargs):
        cls = self.content_type.model_class()
        name = self.name
        super().delete(*args, **kwargs)
        cls._del_deferred_translated_field(name)


class Language(models.Model):
    class Meta:
        verbose_name = _('Language')
        verbose_name_plural = _('Languages')
        ordering = ['iso']

    iso = models.CharField(max_length=2, unique=True, primary_key=True)
    is_active = models.BooleanField(_(u'Active'), default=True)

    def __str__(self):
        return self.iso


def prepare_cls_for_translate(cls, attr, trans_mng=None):
    if not issubclass(cls, TranslationsFieldsMixin):
        trans_mng = trans_mng or TranslationsManager()
        cls.__bases__ = (TranslationsFieldsMixin, ) + cls.__bases__
        if CHANGE_DEFAULT_MANAGER and not isinstance(cls._default_manager, TranslationsManager):
            trans_mng.contribute_to_class(cls, trans_mng.default_name)
            cls._meta.default_manager_name = trans_mng.default_name
            # FIXME
            del cls.objects
            trans_mng.contribute_to_class(cls, 'objects')
    cls._add_deferred_translated_field(attr)
