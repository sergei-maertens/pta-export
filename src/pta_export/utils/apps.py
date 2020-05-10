from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = "pta_export.utils"

    def ready(self):
        from . import checks  # noqa
