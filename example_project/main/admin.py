# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-28 20:30:42
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-29 14:04:24
from django.contrib import admin
from tof.decorators import tof_prefetch
from tof.forms import TranslationFieldModelForm

from .models import Vintage, Wine


class TransForm(TranslationFieldModelForm):
    """Example translatable field №3

    This class is example where one field like example №1 and second like example №2
    """
    only_current_lang = ('description',)


@admin.register(Wine)
class WineAdmin(admin.ModelAdmin):
    """Example translatable field №2

    This class is example where translatable field save values to all added languages

    Attributes:
        list_display: [description]
        search_fields: [description]
        form: [description]
    """
    list_display = ('title', 'description', 'active', 'sort')
    search_fields = ('title', )
    form = TransForm


@admin.register(Vintage)
class VintageAdmin(admin.ModelAdmin):
    """Example translatable field №1

    This class is example where translatable field save value only in current language

    Attributes:
        list_display: [description]
    """
    list_display = search_fields = ('wine__title', 'year', 'description')

    def wine__title(self, obj, *args, **kwargs):
        return obj.wine.title

    @tof_prefetch('wine')
    def get_queryset(self, request):
        return super().get_queryset(request)
