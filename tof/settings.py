# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-29 17:39:13
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-26 11:57:39
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

DEFAULT_LANGUAGE = getattr(settings, 'DEFAULT_LANGUAGE', 'en') or 'en'

SITE_ID = getattr(settings, 'SITE_ID', None)

# need support siteid
# maybe beter use information about neighbors
FALLBACK_LANGUAGES = {
    SITE_ID: ('en', 'de', 'ru'),
    'fr': ('nl', ),
}

FALLBACK_LANGUAGES = getattr(settings, 'FALLBACK_LANGUAGES', FALLBACK_LANGUAGES)

if not isinstance(FALLBACK_LANGUAGES, dict):
    raise ImproperlyConfigured('FALLBACK_LANGUAGES is not dict')  # pragma: no cover

for item in FALLBACK_LANGUAGES.values():
    if not isinstance(item, (list, tuple)):
        raise ImproperlyConfigured('FALLBACK_LANGUAGES`s values must list ot tuple')  # pragma: no cover

# can be '__all__', 'current', ['en', 'de'], {'en', ('en', 'de', 'ru')}
DEFAULT_FILTER_LANGUAGE = getattr(settings, 'DEFAULT_FILTER_LANGUAGE', 'current')

CHANGE_DEFAULT_MANAGER = getattr(settings, 'CHANGE_DEFAULT_MANAGER', True)
