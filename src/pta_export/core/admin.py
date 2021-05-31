from django.contrib import admin
from django.contrib.admin import widgets

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
    pass


@admin.register(Vak)
class VakAdmin(admin.ModelAdmin):
    list_display = ("naam", "afkorting", "leerjaren", "weergeven")
    search_fields = ("naam", "afkorting")


@admin.register(Voetnoot)
class VoetnootAdmin(admin.ModelAdmin):
    list_display = ("id", "vak", "noot")
    list_select_related = ("vak",)
    list_filter = ("vak",)


@admin.register(Werk)
class WerkAdmin(admin.ModelAdmin):
    pass
