import html
import logging
from typing import List, Optional, Tuple

from django.db.models import Case, F, Prefetch, Value, When

from .constants import Leerjaren
from .models import Kalender, Toets, Vak

logger = logging.getLogger(__name__)


LEERJAAR_WEGING = {
    Leerjaren.havo_4: ("Weging ED4", "weging_ed4"),
    Leerjaren.vwo_4: ("Weging ED4", "weging_ed4"),
    Leerjaren.havo_5: ("Weging ED5", "weging_ed5"),
    Leerjaren.vwo_5: ("Weging ED5", "weging_ed5"),
    Leerjaren.vwo_6: ("Weging ED6", "weging_ed6"),
}


def export(year: int, leerjaar: int):
    toetsweken = Kalender.objects.get(jaar=year).toetsweken

    # complex sorting - year starts around week 33
    toetsen = (
        Toets.objects.filter(jaar=year, klas=leerjaar)
        .annotate(
            rel_week=Case(
                When(week__gte=33, then=F("week") - Value(33)),
                When(week__lt=33, then=F("week") + Value(-33 + 52)),
            )
        )
        .order_by("rel_week")
    )
    vakken = Vak.objects.prefetch_related(
        Prefetch("toets_set", queryset=toetsen, to_attr="toetsen")
    )

    weging = LEERJAAR_WEGING.get(leerjaar)
    tables = [get_toets_table(vak, toetsweken, weging) for vak in vakken]

    print(tables)


def get_toets_table(
    vak: Vak, toetsweken: List[int], weging: Optional[Tuple[str, str]]
) -> List[List[str]]:
    header = [
        "Code",
        "Onderwerp/Omschrijving",
        "Domein",
        "Periode",
        "Week",
        "Soort werk",
        "Tijd",
        "Weging R4",
    ]

    if weging is not None:
        header.append(weging[0])

    rows = []

    for toets in vak.toetsen:
        periode = toets.periode
        if periode in toetsweken:
            periode = f"{periode} (tw)"

        row = [
            toets.code,
            html.unescape(toets.omschrijving),
            toets.domein,
            periode,
            toets.week,
            toets.soortwerk.naam,
            toets.tijd,
            toets.weging_r4,
        ]

        if weging is not None:
            row.append(getattr(toets, weging[1]))

        assert len(row) == len(header), "Header and row columns mismatch"
        rows.append(row)

    return [header] + rows
