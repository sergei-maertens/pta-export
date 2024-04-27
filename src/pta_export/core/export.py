import logging
from typing import Iterable

from django.db.models import Case, F, Prefetch, When
from django.db.models.functions import Lower
from django.utils import translation

from docx import Document

from .constants import Leerjaren, OverstapActies, Sorteringen, Types
from .document import add_vak, initialize_document
from .models import Kalender, Overstap, Toets, Vak, Voetnoot

logger = logging.getLogger(__name__)


def export(year: int, leerjaar: int) -> Document:
    translation.activate("nl_NL")
    toetsen = (
        Toets.objects.select_related("soortwerk")
        .filter(jaar=year, klas=leerjaar)
        .order_by(
            # first field to order on
            Case(
                When(vak__sortering=Sorteringen.chronological, then=F("lesweek")),
                When(vak__sortering=Sorteringen.by_type, then=F("type")),
                default=F("lesweek"),
            ),
            # second field to order on
            Case(
                When(vak__sortering=Sorteringen.chronological, then=F("type")),
                When(vak__sortering=Sorteringen.by_type, then=F("lesweek")),
                default=F("lesweek"),
            ),
            # and lastly, order on code
            F("code"),
        )
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
            "toets_set",
            queryset=toetsen.filter(type=Types.ED6),
            to_attr="inhaalopdrachten",
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


def create_document(
    year: int,
    leerjaar: int,
    vakken: Iterable[Vak],
) -> Document:
    toetsweek_periodes = Kalender.objects.get(jaar=year).toetsweek_periodes
    document = initialize_document()

    for vak in vakken:
        add_vak(document, vak, year, leerjaar, toetsweek_periodes)

    return document
