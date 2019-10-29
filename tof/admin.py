# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-28 12:30:45
# @Last Modified by:   MaxST
# @Last Modified time: 2019-10-29 16:49:25
from django.contrib import admin

from .models import Language, TranslatableFields, Translations

admin.site.register((Language, Translations, TranslatableFields))
