# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-11-15 19:17:59
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-17 13:50:54
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from main.models import Wine
from mixer.backend.django import mixer

from .models import TranslatableFields, TranslationsFieldsMixin


class TranslatableFieldsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        mixer.blend(Wine, title='Wine 1')

    def test_save(self):
        wine1 = Wine.objects.first()
        self.assertNotIsInstance(wine1, TranslationsFieldsMixin)
        self.create_field()
        self.assertIsInstance(wine1, TranslationsFieldsMixin)

    def test_delete(self):
        self.create_field()
        wine1 = Wine.objects.first()
        self.assertIsInstance(wine1, TranslationsFieldsMixin)
        fld = TranslatableFields.objects.first()
        fld.delete()
        wine1 = Wine.objects.first()
        self.assertNotIsInstance(wine1, TranslationsFieldsMixin)
        self.assertEqual(wine1.title, 'Wine 1')

    def create_field(self):
        ct_wine = ContentType.objects.get_for_model(Wine)
        fld = TranslatableFields.objects.first()
        if not fld:
            mixer.blend(TranslatableFields, name='title', title='Title', content_type=ct_wine)
