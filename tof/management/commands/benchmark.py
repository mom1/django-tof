# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-11-25 13:13:55
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-25 15:24:50
import timeit

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.utils import translation
from main.models import Wine
from mixer.backend.django import mixer
from tof.models import TranslatableField


class Command(BaseCommand):
    def handle(self, *args, **options):
        n = 1000
        nruns = 10
        translation.activate('it')

        ct = ContentType.objects.get_for_model(Wine)
        TranslatableField.objects.all().delete()
        fld = TranslatableField.objects.create(name='title', title='Title', content_type=ct)
        fld.save()
        Wine.objects.all().delete()
        some_models = mixer.cycle(n).blend(Wine, title=mixer.sequence('Wine {0}'))
        with translation.override('it'):
            for instance in some_models:
                instance.title = 'it ' + instance.title
                instance.save()

        print(
            'TOF',
            timeit.timeit("""
for m in Wine.objects.all():
    if not m.title.it.startswith('it'):
        raise ValueError(m.title)
""",
                          globals=globals(),
                          number=1))
        print(
            'TOF',
            timeit.timeit("""
for m in Wine.objects.all():
    if not m.title.it.startswith('it'):
        raise ValueError(m.title)
""",
                          globals=globals(),
                          number=nruns) / nruns)
