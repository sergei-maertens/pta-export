from datetime import date, datetime
from typing import Optional

from django import forms
from django.db import models


class Latin1ButActuallyCP1252CharField(models.CharField):
    def from_db_value(self, value, expression, connection):
        return value.encode("windows-1252").decode("utf-8")


class IntegerDateField(models.IntegerField):
    def from_db_value(self, value, expression, connection) -> Optional[date]:
        if value is None or value == 0:
            return None
        return datetime.fromtimestamp(value).date()

    def value_to_string(self, obj):
        val = self.value_from_object(obj)
        return "" if val is None else val.isoformat()

    def formfield(self, **kwargs):
        return super().formfield(**{"form_class": forms.DateField, **kwargs,})
