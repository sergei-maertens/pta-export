from django.db import models


class Latin1ButActuallyCP1252CharField(models.CharField):

    def from_db_value(self, value, expression, connection):
        return value.encode("windows-1252").decode("utf-8")
