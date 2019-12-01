# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-11-26 19:55:31
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-29 12:04:04
from django.core.exceptions import ValidationError
from django.forms.fields import CharField, MultiValueField
from django.utils.translation import get_language

from .forms import TranslatableFieldHiddenWidget, TranslatableFieldWidget
from .utils import TranslatableText


class TranslatableFieldFormField(MultiValueField):
    widget = TranslatableFieldWidget
    hidden_widget = TranslatableFieldHiddenWidget

    def __init__(self, field=None, *args, **kwargs):
        fld = (field or CharField(*args, **kwargs))
        fld.widget.attrs.update({'lang': get_language()})
        widget = self.widget(fld.widget)
        super().__init__((fld,), widget=widget)

    def compress(self, data_list):
        trans = TranslatableText()
        vars(trans).update({key if key else get_language(): val for key, val in data_list})
        return trans

    def clean(self, value):
        clean_data = []
        errors = []
        if self.disabled and not isinstance(value, list):
            value = self.widget.decompress(value)
        if not value or isinstance(value, (list, tuple)):
            if not value or not [v for v in value if v[1] not in self.empty_values]:
                if self.required:
                    raise ValidationError(self.error_messages['required'], code='required')
                else:
                    return self.compress([])
        else:
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        for lang, field_value in value:
            if field_value in self.empty_values:
                if self.require_all_fields:
                    # Raise a 'required' error if the MultiValueField is
                    # required and any field is empty.
                    if self.required:
                        raise ValidationError(self.error_messages['required'], code='required')
                elif self.fields[0].required:
                    # Otherwise, add an 'incomplete' error to the list of
                    # collected errors and skip field cleaning, if a required
                    # field is empty.
                    if self.fields[0].error_messages['incomplete'] not in errors:
                        errors.append(self.fields[0].error_messages['incomplete'])
                    continue
            try:
                clean_data.append((lang, self.fields[0].clean(field_value)))
            except ValidationError as e:
                # Collect all validation errors in a single list, which we'll
                # raise at the end of clean(), rather than raising a single
                # exception for the first error we encounter. Skip duplicates.
                errors.extend(m for m in e.error_list if m not in errors)
        if errors:
            raise ValidationError(errors)

        out = self.compress(clean_data)
        self.validate(out)
        self.run_validators(out)
        return out
