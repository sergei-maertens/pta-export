import html
import logging
import tempfile
from typing import Iterable, List, Optional, Tuple

from django.db.models import Case, F, Prefetch, Value, When
from django.utils.text import capfirst

from docx import Document
from docx.enum.section import WD_ORIENT

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

    doc = create_document(year, leerjaar, vakken)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        doc.save(tmp.name)
        print(f"Output in: {tmp.name}")


def create_document(year: int, leerjaar: int, vakken: Iterable[Vak],) -> Document:
    toetsweken = Kalender.objects.get(jaar=year).toetsweken
    weging = LEERJAAR_WEGING.get(leerjaar)
    _leerjaar = Leerjaren.labels[leerjaar]
    school_year = f"{year}-{year + 1}"

    document = Document()

    # set to landscape
    section = document.sections[-1]
    new_width, new_height = section.page_height, section.page_width
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width = new_width
    section.page_height = new_height

    # add the document title
    document.add_heading(f"PTAs {_leerjaar} {year}", level=0)

    for vak in vakken:
        header = f"PTA\t{capfirst(vak.naam)}\t{_leerjaar}\t{school_year}"
        document.add_heading("", level=1).add_run(header).bold = True

        [header, *rows] = get_toets_table(vak, toetsweken, weging)

        table = document.add_table(rows=len(rows) + 1, cols=len(header))

        header_cells = table.rows[0].cells
        for index, title in enumerate(header):
            header_cells[index].text = title
            _make_bold(header_cells[index])

        for index, row in enumerate(rows, 1):
            row_cells = table.rows[index].cells
            for _index, content in enumerate(row):
                row_cells[_index].text = str(content)
            _make_bold(row_cells[0])

        document.add_page_break()

    return document


def _make_bold(cell):
    cell.paragraphs[0].runs[0].font.bold = True


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
            toets.week or "",
            toets.soortwerk.naam,
            toets.tijd,
            toets.weging_r4 or "",
        ]

        if weging is not None:
            row.append(getattr(toets, weging[1]) or "")

        assert len(row) == len(header), "Header and row columns mismatch"
        rows.append(row)

    return [header] + rows
