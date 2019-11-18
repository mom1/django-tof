# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-28 20:30:42
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-18 15:11:01
from django.views.generic import TemplateView

from .models import Wine


class Index(TemplateView):
    extra_context = {'wines': Wine.objects.all()}
    template_name = 'main/index.html'
