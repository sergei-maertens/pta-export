from django.contrib import admin
from django.contrib.admin import widgets

from .constants import ExportModes
from .fields import IntegerDateField
from .models import Kalender, Overstap, Toets, User, Vak, Voetnoot, Werk


@admin.register(Kalender)
class KalenderAdmin(admin.ModelAdmin):
    pass


@admin.register(Overstap)
class OverstapAdmin(admin.ModelAdmin):
    list_display = (
        "jaar",
        "klas",
        "cohort",
        "vak",
        "weging_ed4",
        "oude_toets",
        "actie",
    )
    list_filter = ("jaar", "vak", "klas")
    list_select_related = ("vak", "oude_toets")
    raw_id_fields = ("oude_toets",)


@admin.register(Toets)
class ToetsAdmin(admin.ModelAdmin):
    list_display = (
        "jaar",
        "klas",
        "cohort",
        "vak",
        "type",
        "code",
        "omschrijving",
        "domein",
        "week",
        "lesweek",
        "weging_ed4",
        "weging_ed5",
        "weging_ed6",
        "weging_r4",
    )
    list_select_related = ("vak",)
    list_filter = ("jaar", "vak", "klas")
    formfield_overrides = {
        IntegerDateField: {"widget": widgets.AdminDateWidget},
    }


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("naam", "afkorting", "email", "actief", "access", "sector")
    search_fields = ("email", "naam")
    list_filter = ("access", "sector")


@admin.register(Vak)
class VakAdmin(admin.ModelAdmin):
    list_display = ("naam", "afkorting", "export_mode", "weergeven", "sortering")
    search_fields = ("naam", "afkorting")

    @admin.display(description="exportmode")
    def export_mode(self, obj: Vak) -> str:
        return ExportModes(obj.export_bit).label


@admin.register(Voetnoot)
class VoetnootAdmin(admin.ModelAdmin):
    list_display = ("id", "vak", "noot")
    list_select_related = ("vak",)
    list_filter = ("vak",)


@admin.register(Werk)
class WerkAdmin(admin.ModelAdmin):
    pass
