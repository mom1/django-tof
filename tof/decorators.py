# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-11-17 15:03:06
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-18 12:59:06
from functools import wraps

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.translation import get_language

from .settings import DEFAULT_FILTER_LANGUAGE, DEFAULT_LANGUAGE


def tof_prefetch(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        query_set = func(*args, **kwargs)
        return query_set.prefetch_related('_translations__field', '_translations__lang')

    return wrapper


def tof_filter(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        from .models import TranslationFieldMixin
        new_args, new_kwargs = args, kwargs
        if issubclass(self.model, TranslationFieldMixin):
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
        from .models import Translation
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
        new_val = Translation.objects.filter(query).values_list('object_id', flat=True)
        return 'id__in', new_val, True
    return key, value, False
