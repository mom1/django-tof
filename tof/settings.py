# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-29 17:39:13
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-05 13:08:07
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

DEFAULT_LANGUAGE = getattr(settings, 'DEFAULT_LANGUAGE', 'en')
if not DEFAULT_LANGUAGE:
    raise ImproperlyConfigured('DEFAULT_LANGUAGE cannot be empty.')

SITE_ID = getattr(settings, 'SITE_ID', None)

# need support siteid
# maybe beter use information about neighbors
FALLBACK_LANGUAGES = {
    SITE_ID: ('en', 'de', 'ru'),
    'fr': ('nl', ),
}
FALLBACK_LANGUAGES = getattr(settings, 'DEFAULT_LANGUAGE', FALLBACK_LANGUAGES)
