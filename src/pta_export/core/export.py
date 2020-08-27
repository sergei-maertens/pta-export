import logging
from typing import Iterable

from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.models import Prefetch
from django.db.models.functions import Lower
from django.utils import translation

from docx import Document

from .document import initialize_document, add_vak
from .models import Kalender, Toets, Vak, Voetnoot

logger = logging.getLogger(__name__)


def export(year: int, leerjaar: int) -> Document:
    translation.activate("nl_NL")
    toetsen = (
        Toets.objects.select_related("soortwerk")
        .filter(jaar=year, klas=leerjaar)
        .order_by("lesweek")
    )
    voetnoten = Voetnoot.objects.order_by("id")
    vakken = Vak.objects.prefetch_related(
        Prefetch("toets_set", queryset=toetsen, to_attr="toetsen"),
        Prefetch("voetnoot_set", queryset=voetnoten, to_attr="voetnoten"),
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
