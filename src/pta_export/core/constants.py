from django.db import models


class Maanden(models.IntegerChoices):
    empty = 0, ""
    januari = 1
    februari = 2
    maart = 3
    april = 4
    mei = 5
    juni = 6
    juli = 7
    augustus = 8
    september = 9
    oktober = 10
    november = 11
    december = 12


class Dagen(models.IntegerChoices):
    zondag = 0
    maandag = 1
    dinsdag = 2
    woensdag = 3
    donderdag = 4
    vrijdag = 5
    zaterdag = 6
    zondag2 = 7, "zondag"


class Leerjaren(models.IntegerChoices):
    empty = 0, ""
    havo_4 = 1, "4 Havo"
    havo_5 = 2, "5 Havo"
    vwo_3 = 16, "3 VWO"
    vwo_4 = 3, "4 VWO"
    vwo_5 = 4, "5 VWO"
    vwo_6 = 5, "6 VWO"
    overstappers_vwo_5 = 6, "overstappers VWO 5"
    overstappers_vwo_6 = 7, "overstappers VWO 6"


class Types(models.IntegerChoices):
    empty = 0, ""
    R = 1, "rapporttoets"
    V = 2, "voortgangstoets"
    T = 3, "herkansbare toets"
    P = 4, "praktische opdracht"
    H = 5, "handelingsopdracht"
    ED4 = 6, "jaarcijfer klas 4"
    ED5 = 7, "jaarcijfer klas 5"
    ED6 = 8, "jaarcijfer klas 6"


class OverstapOpties(models.IntegerChoices):
    empty = 0, ""
    overnemen = 1
    herwaarderen = 2
    inhalen = 3


class Breuken(models.IntegerChoices):
    empty = 0, ""
    one_third = 1, "1/3"
    two_thirds = 2, "2/3"
    one_sixth = 3, "1/6"
    five_sixths = 4, "5/6"
    one_eight = 5, "1/8"
    three_eights = 6, "3/8"
    five_eights = 7, "5/8"
    seven_eights = 8, "7/8"
    one_twelfth = 9, "1/12"
    five_twelfths = 10, "5/12"
    saven_twelfths = 11, "7/12"
    eleven_twelfths = 12, "11/12"


class OverstapActies(models.IntegerChoices):
    overnemen = 1, "overnemen"
    herwaarderen = 2, "herwaarderen"
    inhalen = 3, "inhalen"
    meemaken = 4, "meemaken met H5"


class Sorteringen(models.IntegerChoices):
    chronological = 1, "chronologisch"
    by_type = 2, "op type"


class ExportModes(models.TextChoices):
    no_export = "0", "niet exporteren"
    table = "1", "tabel exporteren"
    remark_completed_earlier = "2", "opmerking eerder afgerond"
    remark_vwo = "3", "opmerking afronding op VWO niveau"
