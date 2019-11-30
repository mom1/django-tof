# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-30 14:19:55
# @Last Modified by:   MaxST
# @Last Modified time: 2019-12-01 01:18:21
from django.utils.html import html_safe
from django.utils.translation import get_language
from itertools import zip_longest
from .settings import DEFAULT_LANGUAGE, FALLBACK_LANGUAGES, SITE_ID


@html_safe
class TranslatableText(str):
    def __getattr__(self, attr):
        if len(attr) == 2:
            attrs = vars(self)
            for lang in self.get_fallback_languages(attr):
                if lang in attrs:
                    return attrs[lang]
            return attrs.get('_origin') or ''
        raise AttributeError(attr)

    def __getitem__(self, key):
        return str(self)[key]

    def __str__(self):
        return getattr(self, self.get_lang(), '')

    def __repr__(self):
        return f"'{self}'"

    def __eq__(self, other):
        return str(self) == str(other)

    def __add__(self, other):
        return f'{self}{other}'

    def __radd__(self, other):
        return f'{other}{self}'

    def __bool__(self):
        return bool(vars(self))

    @staticmethod
    def get_lang():
        lang, *_ = get_language().partition('-')
        return lang

    def get_fallback_languages(self, attr):
        for fallback in (FALLBACK_LANGUAGES.get(attr) or (), FALLBACK_LANGUAGES.get(SITE_ID) or ()):
            yield from (lang for lang in fallback if lang != attr)
        yield DEFAULT_LANGUAGE


class MultiKeyDict:
    __slots__ = ('dicts',)

    def __init__(self, **kwargs):
        self.dicts = []

    def __getitem__(self, key):
        for d in self.dicts:
            val = d.get(key)
            if val:
                return val
        raise KeyError

    def __setitem__(self, keys, value):
        for key, d in zip_longest(keys, self.dicts, fillvalue=None):
            if key:
                if d:
                    d[key] = value
                else:
                    self.dicts.append({key: value})

    def setdefault(self, keys, value):
        self[keys] = value
        return value

    def delete(self, keys):
        for key in keys:
            for i, d in enumerate(self.dicts):
                d.pop(key, None)
                if not d:
                    del self.dicts[i]

    def values(self):
        return {**self.dicts[0]}.values() if self.dicts else self.dicts

    def get(self, key, def_val=None):
        try:
            return self[key]
        except KeyError:
            return def_val

    def __bool__(self):
        return any(self.dicts)
