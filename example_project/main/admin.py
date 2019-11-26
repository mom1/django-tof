# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-28 20:30:42
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-26 11:42:17
from django.contrib import admin
from tof.decorators import tof_prefetch

from .models import Vintage, Wine


@admin.register(Wine)
class WineAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'active', 'sort')
    search_fields = ('title', )


@admin.register(Vintage)
class VintageAdmin(admin.ModelAdmin):
    list_display = search_fields = ('wine__title', 'year')

    def wine__title(self, obj, *args, **kwargs):
        return obj.wine.title

    @tof_prefetch('wine')
    def get_queryset(self, request):
        return super().get_queryset(request)
