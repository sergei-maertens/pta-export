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
    havo_4 = 1, "4 havo"
    havo_5 = 2, "5 havo"
    vwo_4 = 3, "4 vwo"
    vwo_5 = 4, "5 vwo"
    vwo_6 = 5, "6 vwo"
    overstappers_vwo_5 = 6, "overstappers vwo 5"
    overstappers_vwo_6 = 7, "overstappers vwo 6"
    have_vwo_1 = 11, "1 havo/vwo"
    gym_ath_1 = 12, "1 gynmasium/atheneum"
    have_vwo_2 = 13, "2 havo/vwo"
    gym_ath_2 = 14, "2 gynmasium/atheneum"
    havo_3 = 15, "3 havo"
    gym_ath_3 = 16, "3 gymnasium/atheneum"  # vwo_3 before
    lo_1 = 21, "1 leerwegondersteunend"
    bk_1 = 22, "1 basis/kader"
    tl_havo_1 = 23, "1 TL/havo"
    lo_2 = 24, "2 leerwegondersteunend"
    bk_2 = 25, "2 basis/kader"
    tl_havo_2 = 26, "2 TL/havo"
    lwt_3 = 27, "3 leerwerktraject"
    basis_3 = 28, "3 basis"
    kader_3 = 29, "3 kader"
    tl_3 = 30, "3 theoretisch"
    basis_4 = 32, "4 basis"
    kader_4 = 33, "4 kader"
    tl_4 = 34, "4 theoretisch"


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
