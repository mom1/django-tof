# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-28 20:30:42
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-28 18:06:46
from django.contrib import admin
from tof.decorators import tof_prefetch
from tof.forms import TranslationFieldModelForm

from .models import Vintage, Wine


@admin.register(Wine)
class WineAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'active', 'sort')
    search_fields = ('title', )
    form = TranslationFieldModelForm


@admin.register(Vintage)
class VintageAdmin(admin.ModelAdmin):
    list_display = search_fields = ('wine__title', 'year', 'description')

    def wine__title(self, obj, *args, **kwargs):
        return obj.wine.title

    @tof_prefetch('wine')
    def get_queryset(self, request):
        return super().get_queryset(request)
