# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-30 14:19:55
# @Last Modified by:   MaxST
# @Last Modified time: 2019-12-01 17:46:28
from django.utils.html import html_safe
from django.utils.translation import get_language
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
    __slots__ = ('keys', 'vals', 'len_val')

    def __init__(self, **kwargs):
        self.keys = {}
        self.vals = []
        self.len_val = 0

    def __getitem__(self, key):
        try:
            return self.vals[self.keys.get(key)]
        except (IndexError, TypeError):
            raise KeyError

    def __setitem__(self, keys, value):
        i = min(self.keys.setdefault(key, self.len_val) for key in keys)
        if i == self.len_val:
            self.vals.append(value)
            self.len_val += 1
        self.vals[i] = value

    def __delitem__(self, keys):
        for key in keys:
            i = self.keys[key]
            del self.keys[key]
            if i not in self.keys.values():
                self.vals[i] = None

    def setdefault(self, keys, value):
        try:
            val = self[keys]
        except KeyError:
            val = self[keys] = value
        return val

    def values(self):
        yield from (i for i in self.vals if i)

    def get(self, key, def_val=None):
        try:
            return self[key]
        except KeyError:
            return def_val

    def __bool__(self):
        return bool(self.keys)
