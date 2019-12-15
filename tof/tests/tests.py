# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-11-15 19:17:59
# @Last Modified by:   MaxST
# @Last Modified time: 2019-12-15 14:23:41
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.views.main import SEARCH_VAR
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db.models import Q
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils.translation import activate, override
from main.models import Vintage, Wine, Winery
from mixer.backend.django import mixer
from tof.admin import (
    ContentTypeAdmin, LanguageAdmin, TranslatableFieldAdmin, TranslationAdmin,
)
from tof.fields import TranslatableFieldFormField
from tof.models import (
    Language, TranslatableField, Translation, TranslationFieldMixin,
)
from tof.settings import FALLBACK_LANGUAGES
from tof.utils import TranslatableText

site = admin.AdminSite(name='admin')

site.register(User, UserAdmin)
site.register(ContentType, ContentTypeAdmin)
site.register(Language, LanguageAdmin)
site.register(TranslatableField, TranslatableFieldAdmin)
site.register(Translation, TranslationAdmin)


def create_field(name='title', cls=None):
    ct = ContentType.objects.get_for_model(cls or Wine)
    fld = TranslatableField.objects.filter(content_type=ct).first()
    if not fld:
        mixer.blend(TranslatableField, name=name, title=name.title(), content_type=ct)


def clean_model(cls, attr='title'):
    if issubclass(cls, TranslationFieldMixin):
        for fld in {**cls._meta._field_tof['by_id']}.values():
            fld.remove_translation_from_class()


class TranslatableFieldTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        clean_model(Wine)
        clean_model(LogEntry)
        mixer.blend(Wine, title='Wine 1')

    def test_save(self):
        wine1 = Wine.objects.first()
        log = LogEntry.objects.first()
        self.assertNotIsInstance(wine1, TranslationFieldMixin)
        self.assertNotIsInstance(log, TranslationFieldMixin)
        self.assertIsNone(vars(LogEntry._meta).get('_field_tof'))
        create_field()
        self.assertIsInstance(wine1, TranslationFieldMixin)
        self.assertIsNotNone(vars(Wine._meta).get('_field_tof'))
        self.assertIsNone(vars(LogEntry._meta).get('_field_tof'))
        create_field('change_message', LogEntry)
        self.assertIsNotNone(vars(LogEntry._meta).get('_field_tof'))

    def test_delete(self):
        create_field()
        wine1 = Wine.objects.first()
        self.assertIsInstance(wine1, TranslationFieldMixin)
        fld = TranslatableField.objects.first()
        fld.delete()
        wine1 = Wine.objects.first()
        self.assertNotIsInstance(wine1, TranslationFieldMixin)
        self.assertEqual(wine1.title, 'Wine 1')
        wine2 = mixer.blend(Wine, title='Wine 2')
        self.assertEqual(wine2.title, 'Wine 2')

    def test_str(self):
        create_field()
        fld = TranslatableField.objects.first()
        self.assertEqual(str(fld), 'wine|Title')


class TranslationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        clean_model(Wine)
        mixer.blend(Wine, title='Wine 1')
        create_field()

    def test_str(self):
        fld = TranslatableField.objects.first()
        lang_en = Language.objects.get(iso='en')
        new_title = 'Wine 1 en'
        wine1 = Wine.objects.first()

        self.assertEqual(wine1.title, 'Wine 1')

        trans = mixer.blend(Translation, content_object=wine1, field=fld, lang=lang_en, value=new_title)
        str_make = f'{wine1}.{fld.name}.{lang_en} = "{new_title}"'
        self.assertEqual(str(trans), str_make)


class TranslationFieldMixinTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        clean_model(Wine)
        mixer.blend(Wine, title='Wine 1')
        create_field()

    def test_save(self):
        wine1 = Wine.objects.first()
        title_de = 'Wine 1 de'
        title_en = 'Wine 1 en'
        title_nl = 'Wine 1 en'
        with override('de'):
            wine1.title = title_de
            wine1.save()

        wine1 = Wine.objects.first()
        self.assertEqual(wine1.title.de, title_de)
        value = TranslatableText()
        vars(value).update({'en': title_en, 'nl': title_nl})
        wine1.title = value
        wine1.save()
        wine1 = Wine.objects.first()
        self.assertEqual(wine1.title.en, title_en)
        self.assertEqual(wine1.title.nl, title_nl)

    def test_get(self):
        self.assertIsInstance(Wine.title, TranslatableField)

    def test_prefetch(self):
        wine1 = Wine.objects.first()
        wine1.title = f'{wine1.title}'
        wine1.save()
        with self.assertNumQueries(2):
            for wine in Wine.objects.all():
                self.assertIsNotNone(wine.title)
        mixer.cycle(5).blend(Wine, title=mixer.sequence('Wine {0}'))
        with override('en'):
            for wine in Wine.objects.all():
                wine.title = f'{wine.title} en'
                wine.save()
        with self.assertNumQueries(2):
            for wine in Wine.objects.all():
                self.assertIsNotNone(wine.title.en)


class FilterTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        clean_model(Wine)
        mixer.blend(Wine, title='Wine 1')
        create_field()

    def test_behavior(self):
        wine1 = Wine.objects.first()
        title_de = 'Wine 1 de'
        title_nl = 'Wine 1 nl'
        for title in (title_de, title_nl):
            with override(title.split()[-1]):
                wine1.title = title
                wine1.save()

        wine1 = Wine.objects.first()

        with override('nl'):
            self.assertEqual(str(wine1.title), title_nl)

        with override('fr'):
            self.assertEqual(str(wine1.title), title_nl)

        with override('de'):
            serch_wine = Wine.objects.filter(title=title_de).first()
            self.assertEqual(title_de, str(serch_wine.title))
            serch_wine = Wine.objects.exclude(title=title_de).first()
            self.assertIsNone(serch_wine)
            serch_wine = Wine.objects.get(title=title_de)
            self.assertEqual(title_de, str(serch_wine.title))
            serch_wine = Wine.objects.filter(Q(title=title_de)).first()
            self.assertEqual(title_de, str(serch_wine.title))

            serch_wine = Wine.objects.filter(title=title_nl).first()
            self.assertIsNone(serch_wine)
            from tof import decorators
            decorators.DEFAULT_FILTER_LANGUAGE = '__all__'
            serch_wine = Wine.objects.filter(title=title_nl).first()
            self.assertEqual(wine1, serch_wine)
            decorators.DEFAULT_FILTER_LANGUAGE = 'nl'
            serch_wine = Wine.objects.filter(title=title_nl).first()
            self.assertEqual(wine1, serch_wine)
            decorators.DEFAULT_FILTER_LANGUAGE = ('nl', )
            serch_wine = Wine.objects.filter(title=title_nl).first()
            self.assertEqual(wine1, serch_wine)
            decorators.DEFAULT_FILTER_LANGUAGE = {'de': ('nl', )}
            serch_wine = Wine.objects.filter(title=title_nl).first()
            self.assertEqual(wine1, serch_wine)
            decorators.DEFAULT_FILTER_LANGUAGE = set()
            serch_wine = Wine.objects.filter(title=title_de).first()
            self.assertEqual(wine1, serch_wine)


class TranslatableTextTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        clean_model(Wine)
        mixer.blend(Wine, title='Wine 1')
        create_field()

    def test_common(self):
        wine1 = Wine.objects.first()
        title_nl = 'Wine 1 nl'
        for title in (title_nl, ):
            with override(title.split()[-1]):
                wine1.title = title
                wine1.save()

        val = wine1.title

        self.assertIsInstance(val, TranslatableText)
        self.assertEqual(val, 'Wine 1')
        self.assertEqual(val[0], 'W')
        self.assertEqual(val + '1', 'Wine 11')
        self.assertEqual('1' + val, '1Wine 1')
        self.assertEqual(repr(val), f"'{val}'")
        self.assertEqual(str(val), val.__html__())
        self.assertFalse(hasattr(val, 'resolve_expression'))
        self.assertFalse(hasattr(val, 'prepare_database_save'))
        FALLBACK_LANGUAGES['aa'] = ('nl', )
        with override('aa'):
            self.assertEqual(str(val), title_nl)
        del wine1.title
        self.assertEqual(wine1.title, 'Wine 1')


class Benchmark(TestCase):
    def test_benchmark(self):
        call_command('benchmark')


class ModelAdminTests(TestCase):
    factory = RequestFactory()

    @classmethod
    def setUpTestData(cls):
        activate('en')
        cls.superuser = User.objects.create_superuser(username='super', email='a@b.com', password='xxx')

    def setUp(self):
        clean_model(Wine)
        mixer.blend(Wine, title='Wine 1')
        create_field()
        self.site = AdminSite()

    def test_search_result(self):
        wine = ContentType.objects.get_for_model(Wine)
        vintage = ContentType.objects.get_for_model(Vintage)
        winery = ContentType.objects.get_for_model(Winery)
        m = ContentTypeAdmin(ContentType, site)
        request = self.factory.get('/', data={SEARCH_VAR: 'tof'})
        request.user = self.superuser
        cl = m.get_changelist_instance(request)
        self.assertCountEqual(cl.queryset, [])

        request = self.factory.get('/', data={SEARCH_VAR: 'main'})
        request.user = self.superuser
        cl = m.get_changelist_instance(request)
        self.assertCountEqual(cl.queryset, [vintage, wine, winery])

        m = LanguageAdmin(Language, site)
        lang_aa = Language.objects.get(iso='aa')
        request = self.factory.get('/', data={SEARCH_VAR: 'aa', IS_POPUP_VAR: '1'})
        request.user = self.superuser
        cl = m.get_changelist_instance(request)
        self.assertCountEqual(cl.queryset, [lang_aa])

        lang_aa.is_active = False
        lang_aa.save()

        request = self.factory.get('/', data={SEARCH_VAR: 'aa', IS_POPUP_VAR: '1'})
        request.user = self.superuser
        cl = m.get_changelist_instance(request)
        self.assertCountEqual(cl.queryset, [])

        request = self.factory.get('/autocomplete/', data={SEARCH_VAR: 'aa'})
        request.user = self.superuser
        cl = m.get_changelist_instance(request)
        self.assertCountEqual(cl.queryset, [])

    def test_delete_qs(self):
        request = self.factory.get('/')
        request.user = self.superuser
        m = TranslatableFieldAdmin(TranslatableField, site)
        m.delete_queryset(request, TranslatableField.objects.all())
        wine1 = Wine.objects.first()
        self.assertNotIsInstance(wine1, TranslationFieldMixin)

    def test_response(self):
        # TranslatableFieldAdmin
        ct = ContentType.objects.get_for_model(Wine)
        field = TranslatableField.objects.first()
        self.client.force_login(self.superuser)
        url = reverse('admin:tof_translatablefield_change', args=(field.pk, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(url, data={'id_ct': ct.pk})
        self.assertEqual(response.json(), {'pk': 7, 'fields': ['title', 'title', 'title', 'title', 'description']})  # WTF?
        response = self.client.get(url, data={'id_ct': 999})
        self.assertTrue('errors' in response.json())
        # TranslationAdmin
        wine1 = Wine.objects.first()
        wine1.title = 'Wine 1 en'
        wine1.save()
        trans = Translation.objects.first()
        url = reverse('admin:tof_translation_change', args=(trans.pk, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(url, data={'field_id': field.pk})
        url_auto = reverse('admin:main_wine_autocomplete')
        self.assertEqual(response.json(), {
            'pk': field.content_type.pk,
            'url': url_auto,
            'text': '',
        })
        response = self.client.get(url, data={'field_id': field.pk, 'id_obj': wine1.pk})
        self.assertEqual(response.json(), {'pk': field.content_type.pk, 'text': str(wine1), 'url': url_auto})
        response = self.client.get(url, data={'field_id': 999, 'id_obj': wine1.pk})
        self.assertTrue('errors' in response.json())
        #
        wine = Wine.objects.first()
        url = reverse('admin:main_wine_change', args=(wine.pk, ))
        response = self.client.get(url)
        self.assertContains(response, 'translatable_fields_widget.js')
        self.assertContains(response, 'en_id_title_en')


class FieldTests(TestCase):
    def test_field(self):
        activate('en')
        fld = TranslatableFieldFormField()
        data = [['en', 'Wine en'], ['de', 'Wine de']]
        cmps = fld.clean(data)
        self.assertEqual(dict(data), vars(cmps))
        with self.assertRaises(ValidationError):
            fail_data = data.copy()
            fail_data[0] = ['en', '']
            cmps = fld.clean(fail_data)

        fld.required = False
        self.assertEqual('', fld.clean(None))
        fld.required = True

        fld.require_all_fields = False
        cmps = fld.clean(fail_data)
        self.assertEqual(dict(fail_data), vars(cmps))
        fld.fields[0].required = True
        with self.assertRaises(ValidationError):
            fld.clean(fail_data)
        fld.fields[0].required = False
        fld.require_all_fields = True

        with self.assertRaises(ValidationError):
            cmps = fld.clean(None)

        val = TranslatableText()
        vars(val).update(dict(data))
        with self.assertRaises(ValidationError):
            fld.clean(val)
        fld.disabled = True
        fld.required = False
        self.assertEqual('Wine en', fld.clean(val))
        fld.required = True
        fld.disabled = False
        with self.assertRaises(ValidationError):
            fail_data[0][1] += '\x00'
            fld.clean(fail_data)
