import logging
from typing import Iterable

from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.models import Prefetch
from django.db.models.functions import Lower
from django.utils import translation

from docx import Document

from .constants import Leerjaren, OverstapActies
from .document import add_vak, initialize_document
from .models import Kalender, Overstap, Toets, Vak, Voetnoot

logger = logging.getLogger(__name__)


def export(year: int, leerjaar: int) -> Document:
    translation.activate("nl_NL")
    toetsen = (
        Toets.objects.select_related("soortwerk")
        .filter(jaar=year, klas=leerjaar)
        .order_by("lesweek")
    )
    voetnoten = Voetnoot.objects.order_by("id")
    overstappen = (
        Overstap.objects.filter(jaar=year, klas=leerjaar)
        .select_related("oude_toets")
        .order_by("oude_toets__klas", "oude_toets__code")
    )
    vakken = Vak.objects.prefetch_related(
        Prefetch("toets_set", queryset=toetsen, to_attr="toetsen"),
        Prefetch("voetnoot_set", queryset=voetnoten, to_attr="voetnoten"),
        Prefetch(
            "overstap_set",
            queryset=(
                overstappen.filter(
                    actie__in=(OverstapActies.overnemen, OverstapActies.herwaarderen)
                )
            ),
            to_attr="overnemen_herwaarderen",
        ),
        Prefetch(
            "overstap_set",
            queryset=overstappen.filter(
                actie=OverstapActies.inhalen, oude_toets__isnull=False
            ),
            to_attr="inhalen",
        ),
        Prefetch(
            "toets_set", queryset=toetsen.filter(type=8), to_attr="inhaalopdrachten",
        ),
        Prefetch(
            "toets_set",
            queryset=(
                Toets.objects.exclude(soortwerk=12)
                .filter(jaar=year, klas=Leerjaren.havo_5)
                .order_by("code")
            ),
            to_attr="h5_toetsen",
        ),
        Prefetch(
            "overstap_set",
            queryset=(
                overstappen.filter(oude_toets__isnull=False).select_related("h5_toets")
            ),
            to_attr="overstappen_vwo6",
        ),
    ).order_by(Lower("naam"))
    doc = create_document(year, leerjaar, vakken)
    translation.deactivate()
    return doc


def create_document(year: int, leerjaar: int, vakken: Iterable[Vak],) -> Document:
    toetsweek_periodes = Kalender.objects.get(jaar=year).toetsweek_periodes
    logo_path = staticfiles_storage.path("img/logopta.jpg")

    document = initialize_document()

    for vak in vakken:
        add_vak(document, logo_path, vak, year, leerjaar, toetsweek_periodes)

    return document
