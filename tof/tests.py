# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-11-15 19:17:59
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-18 10:11:44
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.test import TestCase
from django.utils.translation import override

from main.models import Wine
from mixer.backend.django import mixer

from .models import (
    Language, TranslatableFields, Translations,
    TranslationsFieldsMixin, restore_cls_after_translate,
)
from .settings import FALLBACK_LANGUAGES


def create_field(name='title', cls=None):
    ct_wine = ContentType.objects.get_for_model(cls or Wine)
    fld = TranslatableFields.objects.first()
    if not fld:
        mixer.blend(TranslatableFields, name=name, title=name.title(), content_type=ct_wine)


def clean_model(cls, attr='title'):
    if issubclass(cls, TranslationsFieldsMixin):
        restore_cls_after_translate(cls, attr, False)


class TranslatableFieldsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        clean_model(Wine)
        mixer.blend(Wine, title='Wine 1')

    def test_save(self):
        wine1 = Wine.objects.first()
        self.assertNotIsInstance(wine1, TranslationsFieldsMixin)
        create_field()
        self.assertIsInstance(wine1, TranslationsFieldsMixin)

    def test_delete(self):
        create_field()
        wine1 = Wine.objects.first()
        self.assertIsInstance(wine1, TranslationsFieldsMixin)
        fld = TranslatableFields.objects.first()
        fld.delete()
        wine1 = Wine.objects.first()
        self.assertNotIsInstance(wine1, TranslationsFieldsMixin)
        self.assertEqual(wine1.title, 'Wine 1')
        wine2 = mixer.blend(Wine, title='Wine 2')
        self.assertEqual(wine2.title, 'Wine 2')

    def test_str(self):
        create_field()
        fld = TranslatableFields.objects.first()
        self.assertEqual(str(fld), 'wine|Title')


class TranslationsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        clean_model(Wine)
        mixer.blend(Wine, title='Wine 1')
        create_field()

    def test_str(self):
        fld = TranslatableFields.objects.first()
        lang_en = Language.objects.get(iso='en')
        new_title = 'Wine 1 en'
        wine1 = Wine.objects.first()

        self.assertEqual(wine1.title, 'Wine 1')

        trans = mixer.blend(Translations, content_object=wine1, field=fld, lang=lang_en, value=new_title)
        str_make = f'{wine1}.{fld.name}.{lang_en} = {new_title})'

        self.assertEqual(str(trans), str_make)


class TranslationsFieldsMixinTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        clean_model(Wine)
        mixer.blend(Wine, title='Wine 1')
        create_field()

    def test_save(self):
        wine1 = Wine.objects.first()
        title_de = 'Wine 1 de'
        wine1.title = title_de
        with override('de'):
            wine1.save()

        wine1 = Wine.objects.first()
        self.assertEqual(wine1.title.de, title_de)

    def test_get(self):
        self.assertTrue(isinstance(Wine.title, property))
        Wine._del_deferred_translated_field('jopa')


class DeferredTranslatedAttributeTestCase(TestCase):
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
            self.assertEqual(None, serch_wine)
            serch_wine = Wine.objects.get(title=title_de)
            self.assertEqual(title_de, str(serch_wine.title))
            serch_wine = Wine.objects.filter(Q(title=title_de)).first()
            self.assertEqual(title_de, str(serch_wine.title))

            serch_wine = Wine.objects.filter(title=title_nl).first()
            self.assertEqual(None, serch_wine)
            from . import decorators
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
        for attr in ('resolve_expression', 'as_sql'):
            with self.assertRaises(AttributeError):
                getattr(val, attr)

        self.assertEqual(str(val), 'Wine 1')
        self.assertEqual(repr(val), str(val))
        self.assertEqual(str(val), val.__html__())
        FALLBACK_LANGUAGES['aa'] = 'nl'
        with override('aa'):
            self.assertEqual(str(val), title_nl)
