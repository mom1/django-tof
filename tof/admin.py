# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-28 12:30:45
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-09 20:01:33
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse

from .forms import TranslationsForm
from .models import Language, TranslatableFields, Translations

admin.site.register(Language)


@admin.register(TranslatableFields)
class AdminTranslatableFields(admin.ModelAdmin):
    search_fields = ('name', 'title')


@admin.register(Translations)
class AdminTranslations(admin.ModelAdmin):
    form = TranslationsForm
    list_display = ('content_object', 'lang', 'field', 'value')
    list_filter = ('content_type', )
    fieldsets = ((None, {
        'fields': (('field', 'lang'), 'object_id', 'value'),
    }), (
        'hidden',
        {
            'classes': ('hidden', ),
            'fields': ('content_type', ),
        },
    ))
    autocomplete_fields = ('field', )

    def _changeform_view(self, request, object_id, form_url, extra_context):
        fld_id = request.GET.get('field_id')
        if fld_id:
            try:
                return JsonResponse({'content_type': TranslatableFields.objects.get(id=fld_id).content_type.pk})
            except Exception:
                pass
        return super()._changeform_view(request, object_id, form_url, extra_context)
