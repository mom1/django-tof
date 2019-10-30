# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-28 20:30:42
# @Last Modified by:   MaxST
# @Last Modified time: 2019-10-30 13:38:57
from django.db import models
from django.utils.translation import gettext_lazy as _


class Wine(models.Model):
    class Meta:
        verbose_name = _('wine')
        verbose_name_plural = _('wine-plural')
        ordering = ('title', )

    title = models.CharField(_('Title'), max_length=250, default='', blank=True, null=False)
    description = models.TextField(_('Description'), null=True, blank=True)
    active = models.BooleanField(_('Active'), default=False)
    sort = models.IntegerField(_('Sort'), default=0, blank=True, null=True)

    temperature_from = models.FloatField(_('Temperature_from'), help_text=_('in ° C'), null=True, blank=True)
    temperature_to = models.FloatField(_('Temperature_to'), help_text=_('in ° C'), null=True, blank=True)
