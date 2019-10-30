# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-29 17:39:13
# @Last Modified by:   MaxST
# @Last Modified time: 2019-10-29 19:41:28
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

DEFAULT_TRANSLATE = 'en'

# need support siteid
# maybe beter use information about neighbors
FALLBACK_LANGUAGES = {
    None: ('en', 'de', 'ru'),
    # 'fr': ('nl', )
}
