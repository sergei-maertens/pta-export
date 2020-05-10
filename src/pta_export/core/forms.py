from django import forms

from .constants import Leerjaren
from .models import Kalender


class ExportForm(forms.Form):
    jaar = forms.IntegerField(
        label="Jaar", help_text="Jaar in de kalendar om te exporteren",
    )
    klas = forms.TypedChoiceField(
        label="klas",
        choices=[choice for choice in Leerjaren.choices if choice[0]],
        help_text="Selecteer de klas om te exporteren.",
        coerce=int,
    )

    def clean_jaar(self):
        jaar = self.cleaned_data["jaar"]
        if not Kalender.objects.filter(jaar=jaar).exists():
            raise forms.ValidationError("Er bestaat geen kalender voor dit jaar")
        return jaar
