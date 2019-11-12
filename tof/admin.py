# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-28 12:30:45
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-12 13:46:47
from django.contrib import admin
from django.http import JsonResponse

from .forms import TranslationsForm
from .models import Language, TranslatableFields, Translations
from .views import get_generickey_json


@admin.register(Language)
class AdminLanguage(admin.ModelAdmin):
    search_fields = ('iso_639_1', )


@admin.register(TranslatableFields)
class AdminTranslatableFields(admin.ModelAdmin):
    search_fields = ('name', 'title')

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()


@admin.register(Translations)
class AdminTranslations(admin.ModelAdmin):
    form = TranslationsForm
    list_display = ('content_object', 'lang', 'field', 'value')
    list_filter = ('content_type', )
    fieldsets = ((None, {
        'fields': (
            ('field', 'lang'),
            'object_id',
            'value',
        ),
    }), (
        'hidden',
        {
            'classes': ('hidden', ),
            'fields': ('content_type', ),
        },
    ))
    autocomplete_fields = ('field', 'lang')

    def _changeform_view(self, request, object_id, form_url, extra_context):
        fld_id = request.GET.get('field_id')
        is_objs = request.GET.get('get_objs')
        if fld_id:
            try:
                return JsonResponse({'content_type': TranslatableFields.objects.get(id=fld_id).content_type.pk})
            except Exception:
                pass
        elif is_objs:
            return get_generickey_json(request)
        return super()._changeform_view(request, object_id, form_url, extra_context)
