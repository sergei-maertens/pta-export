from django.contrib import admin

from .models import Kalender, Overstap, Toets, User, Vak, Voetnoot, Werk


@admin.register(Kalender)
class KalenderAdmin(admin.ModelAdmin):
    pass


@admin.register(Overstap)
class OverstapAdmin(admin.ModelAdmin):
    pass


@admin.register(Toets)
class ToetsAdmin(admin.ModelAdmin):
    list_display = ("jaar", "klas", "cohort", "vak", "type", "code", "omschrijving", "domein", "week")
    list_select_related = ("vak",)
    list_filter = ("jaar", "vak", "klas")


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
