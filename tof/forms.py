# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-11-09 13:47:17
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-09 13:58:42
from django import forms


class TranslationsForm(forms.ModelForm):
    class Media:
        js = ('tof/js/translation_form.js', )
