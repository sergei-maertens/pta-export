from django import forms
from django.utils import timezone

from .constants import Leerjaren
from .models import Kalender, User as PtaUser
from .permissions import get_allowed_leerjaren


class ExportForm(forms.Form):
    jaar = forms.IntegerField(
        label="Jaar",
        help_text="Jaar in de kalender om te exporteren",
        initial=lambda: timezone.now().year,
    )
    klas = forms.TypedChoiceField(
        label="klas",
        choices=[choice for choice in Leerjaren.choices if choice[0]],
        help_text="Selecteer de klas om te exporteren.",
        coerce=int,
    )

    def __init__(self, *args, **kwargs):
        pta_user: PtaUser | None = kwargs.pop("pta_user")
        super().__init__(*args, **kwargs)

        leerjaren_choices = get_allowed_leerjaren(pta_user)
        self.fields["klas"].choices = [
            (choice.value, choice.label) for choice in leerjaren_choices
        ]

    def clean_jaar(self):
        jaar = self.cleaned_data["jaar"]
        if not Kalender.objects.filter(jaar=jaar).exists():
            raise forms.ValidationError("Er bestaat geen kalender voor dit jaar")
        return jaar
