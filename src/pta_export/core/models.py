from typing import List

from django.db import models

from .constants import Leerjaren, Types
from .fields import IntegerDateField, Latin1ButActuallyCP1252CharField

TOETSWEEK_FIELDS = (
    "tw11",
    "tw12",
    "tw21",
    "tw22",
    "tw31",
    "tw32",
    "tw41",
    "tw42",
)


TOETSWEEK_PERIODES = {
    1: ["tw11", "tw12"],
    2: ["tw21", "tw22"],
    3: ["tw31", "tw32"],
    4: ["tw41", "tw42"],
}


class Kalender(models.Model):
    id = models.AutoField(db_column="OCK_ID", primary_key=True)
    jaar = models.IntegerField(db_column="OCK_Jaar", blank=True, null=True)
    # values below are week numbers
    begin = models.IntegerField(db_column="OCK_Begin", blank=True, null=True)
    eind = models.IntegerField(db_column="OCK_Eind", blank=True, null=True)
    herfst = models.IntegerField(db_column="OCK_Herfst", blank=True, null=True)
    kerst1 = models.IntegerField(db_column="OCK_Kerst1", blank=True, null=True)
    kerst2 = models.IntegerField(db_column="OCK_Kerst2", blank=True, null=True)
    krokus = models.IntegerField(db_column="OCK_Krokus", blank=True, null=True)
    tulp1 = models.IntegerField(db_column="OCK_Tulp1", blank=True, null=True)
    tulp2 = models.IntegerField(db_column="OCK_Tulp2", blank=True, null=True)
    tw11 = models.IntegerField(db_column="OCK_TW11", blank=True, null=True)
    tw12 = models.IntegerField(db_column="OCK_TW12", blank=True, null=True)
    tw21 = models.IntegerField(db_column="OCK_TW21", blank=True, null=True)
    tw22 = models.IntegerField(db_column="OCK_TW22", blank=True, null=True)
    tw31 = models.IntegerField(db_column="OCK_TW31", blank=True, null=True)
    tw32 = models.IntegerField(db_column="OCK_TW32", blank=True, null=True)
    tw41 = models.IntegerField(db_column="OCK_TW41", blank=True, null=True)
    tw42 = models.IntegerField(db_column="OCK_TW42", blank=True, null=True)
    vrij = models.IntegerField(db_column="OCK_Vrij", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "OC_kalender"
        verbose_name_plural = "kalenders"

    def __str__(self):
        return str(self.jaar)

    @property
    def toetsweken(self) -> List[int]:
        return [getattr(self, field) for field in TOETSWEEK_FIELDS]

    @property
    def toetsweek_periodes(self):
        weeknrs_per_periode = {
            periode: [getattr(self, field) for field in fields]
            for periode, fields in TOETSWEEK_PERIODES.items()
        }
        return weeknrs_per_periode


class Overstap(models.Model):
    id = models.AutoField(db_column="OCO_ID", primary_key=True)
    jaar = models.IntegerField(db_column="OCO_Jaar", blank=True, null=True)
    klas = models.IntegerField(
        db_column="OCO_Klas", choices=Leerjaren.choices, blank=True, null=True,
    )
    vak = models.IntegerField(db_column="OCO_Vak", blank=True, null=True)
    cohort = models.CharField(
        db_column="OCO_Cohort", max_length=15, blank=True, null=True
    )
    user = models.IntegerField(db_column="OCO_User", blank=True, null=True)
    weging_ed4 = models.IntegerField(db_column="OCO_Weging_ED4", blank=True, null=True)
    oudetoets = models.IntegerField(db_column="OCO_Oudetoets", blank=True, null=True)
    actie = models.IntegerField(db_column="OCO_Actie", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "OC_overstap"
        verbose_name_plural = "overstappen"


class Toets(models.Model):
    id = models.AutoField(db_column="OCT_ID", primary_key=True)
    jaar = models.IntegerField(db_column="OCT_Jaar", blank=True, null=True)
    klas = models.IntegerField(
        db_column="OCT_Klas", choices=Leerjaren.choices, blank=True, null=True
    )
    cohort = models.CharField(
        db_column="OCT_Cohort", max_length=15, blank=True, null=True
    )
    vak = models.ForeignKey(
        "Vak", db_column="OCT_Vak", blank=True, null=True, on_delete=models.SET_NULL
    )
    user = models.ForeignKey(
        "User", db_column="OCT_User", blank=True, null=True, on_delete=models.SET_NULL
    )
    type = models.IntegerField(
        db_column="OCT_Type", choices=Types.choices, blank=True, null=True,
    )
    code = models.CharField(db_column="OCT_Code", max_length=6, blank=True, null=True)
    omschrijving = Latin1ButActuallyCP1252CharField(
        db_column="OCT_Omschrijving", max_length=200, blank=True, null=True
    )
    domein = models.CharField(
        db_column="OCT_Domein", max_length=40, blank=True, null=True
    )
    week = models.IntegerField(db_column="OCT_Week", blank=True, null=True)
    lesweek = models.IntegerField(db_column="OCT_Lesweek", blank=True, null=True)
    inleverdatum = IntegerDateField(db_column="OCT_InleverDatum", blank=True, null=True)
    datum = IntegerDateField(db_column="OCT_Datum", blank=True, null=True)
    periode = models.IntegerField(db_column="OCT_Periode", blank=True, null=True)
    soortwerk = models.ForeignKey(
        "Werk",
        db_column="OCT_SoortWerk",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    tijd = models.IntegerField(db_column="OCT_Tijd", blank=True, null=True)
    weging_ed4 = models.IntegerField(db_column="OCT_Weging_ED4", blank=True, null=True)
    weging_ed5 = models.IntegerField(db_column="OCT_Weging_ED5", blank=True, null=True)
    weging_ed6 = models.IntegerField(db_column="OCT_Weging_ED6", blank=True, null=True)
    weging_r4 = models.IntegerField(db_column="OCT_Weging_R4", blank=True, null=True)
    pct = models.IntegerField(db_column="OCT_Pct", blank=True, null=True)
    se = models.CharField(db_column="OCT_SE", max_length=20)
    voetnoot = models.CharField(
        db_column="OCT_Voetnoot", max_length=150, blank=True, null=True
    )
    vbijt = models.IntegerField(db_column="OCT_VbijT")

    class Meta:
        managed = False
        db_table = "OC_toetsen"
        verbose_name_plural = "toetsen"

    def __str__(self):
        return f"{self.jaar} - {self.klas} - {self.vak}"


class User(models.Model):
    id = models.AutoField(db_column="OCU_ID", primary_key=True)
    naam = models.CharField(db_column="OCU_Naam", max_length=50, blank=True, null=True)
    afkorting = models.CharField(
        db_column="OCU_Afkorting", max_length=15, blank=True, null=True
    )
    email = models.CharField(
        db_column="OCU_Email", max_length=50, blank=True, null=True
    )
    password = models.CharField(
        db_column="OCU_Password", max_length=75, blank=True, null=True
    )
    vak1 = models.IntegerField(db_column="OCU_Vak1", blank=True, null=True)
    vak2 = models.IntegerField(db_column="OCU_Vak2", blank=True, null=True)
    vak3 = models.IntegerField(db_column="OCU_Vak3", blank=True, null=True)
    vak4 = models.IntegerField(db_column="OCU_Vak4", blank=True, null=True)
    vak5 = models.IntegerField(db_column="OCU_Vak5", blank=True, null=True)
    actief = models.IntegerField(db_column="OCU_Actief", blank=True, null=True)
    access = models.IntegerField(db_column="OCU_Access", blank=True, null=True)
    lastlogin = models.IntegerField(db_column="OCU_LastLogin", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "OC_users"
        verbose_name_plural = "gebruikers"

    def __str__(self):
        return f"{self.naam} ({self.afkorting})"


class Vak(models.Model):
    id = models.AutoField(db_column="OCV_ID", primary_key=True)
    naam = models.CharField(db_column="OCV_Naam", max_length=50, blank=True, null=True)
    afkorting = models.CharField(
        db_column="OCV_Afkorting", max_length=5, blank=True, null=True
    )
    weergeven = models.IntegerField(db_column="OCV_Weergeven", blank=True, null=True)
    leerjaren = models.CharField(
        db_column="OCV_Leerjaren", max_length=8, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "OC_vakken"
        verbose_name_plural = "vakken"

    def __str__(self):
        return self.naam


class Voetnoot(models.Model):
    id = models.AutoField(db_column="OCVN_ID", primary_key=True)
    vak = models.ForeignKey(
        "Vak", db_column="OCVN_Vak", blank=True, null=True, on_delete=models.SET_NULL
    )
    noot = models.CharField(
        db_column="OCVN_Noot", max_length=800, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "OC_voetnoot"
        verbose_name_plural = "voetnoten"

    def __str__(self):
        return self.noot


class Werk(models.Model):
    id = models.AutoField(db_column="OCW_ID", primary_key=True)
    naam = models.CharField(db_column="OCW_Naam", max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "OC_werk"
        verbose_name_plural = "werken"

    def __str__(self):
        return self.naam
