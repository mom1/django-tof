# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-28 12:30:45
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-12 21:15:47
from django.contrib import admin
from django.http import Http404, JsonResponse
from django.urls import reverse

from .forms import TranslationsForm, TranslatableFieldsForm
from .models import Language, TranslatableFields, Translations
from django.contrib.contenttypes.models import ContentType



@admin.register(Language)
class AdminLanguage(admin.ModelAdmin):
    search_fields = ('iso_639_1', )


@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    search_fields = ('app_label', 'model')


@admin.register(TranslatableFields)
class AdminTranslatableFields(admin.ModelAdmin):
    form = TranslatableFieldsForm
    search_fields = ('name', 'title', )
    list_display = ('content_type', 'name', 'title')

    # fields = ['content_type', 'name', 'title']

    fieldsets = (
        (None, {
            'fields': (
                'content_type',
                'name',
                'title',
            )
        }),
    )

    autocomplete_fields = ('content_type', )
    url_name = '%s:%s_%s_autocomplete'

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()

    def _changeform_view(self, request, object_id, form_url, extra_context):
        # как беруться  фильд айди
        id_ct = request.GET.get('id_ct') # class 'str'
        print(id_ct)

        if id_ct:
            # try:
            ct = ContentType.objects.get_for_id(id_ct) # main | wine
            print(ct)
            model = ct.model_class() # class 'main.models.Wine'
            print(4)
            print(model)
            print(model._meta.get_fields())
            return JsonResponse({
                'pk': ct.pk,
                # как составляется урл? /ru/admin/main/wine/autocomplete/
                'fields': [f.attname for f in model._meta.get_fields()],
            })
            # except Exception:
            # return Http404('Error get content type')
        return super()._changeform_view(request, object_id, form_url, extra_context)


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
    url_name = '%s:%s_%s_autocomplete'

    def _changeform_view(self, request, object_id, form_url, extra_context):
        fld_id = request.GET.get('field_id')

        id_obj = request.GET.get('id_obj')
        if fld_id:
            try:
                print(fld_id)
                ct = TranslatableFields.objects.get(id=fld_id).content_type
                print(ct)
                print(ct.pk)
                model = ct.model_class()
                print(model)
                print(model._meta.get_fields()) # (<django.db.models.fields.AutoField: id>, <django.db.models.fields.CharField: title>,
                # /ru/admin/main/wine/autocomplete/
                print(self.url_name % (self.admin_site.name, model._meta.app_label, model._meta.model_name))
                print(reverse(self.url_name % (self.admin_site.name, model._meta.app_label, model._meta.model_name)))
                print(str(model.objects.get(pk=id_obj)))
                return JsonResponse({
                    'pk': ct.pk,
                    'url': reverse(self.url_name % (self.admin_site.name, model._meta.app_label, model._meta.model_name)),
                    'text': str(model.objects.get(pk=id_obj)) if id_obj else '',
                })
            except Exception:
                return Http404('Error get content type')
        return super()._changeform_view(request, object_id, form_url, extra_context)
