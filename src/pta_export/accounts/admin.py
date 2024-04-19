from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from django.contrib.auth.forms import UserCreationForm as _UserCreationForm

from .models import User


class UserCreationForm(_UserCreationForm):
    class Meta(_UserCreationForm.Meta):
        fields = _UserCreationForm.Meta.fields + ("email",)


@admin.register(User)
class UserAdmin(_UserAdmin):
    add_form = UserCreationForm
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )
