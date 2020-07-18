import html
import logging
from typing import Iterable, List, Optional, Tuple

from django.db.models import Case, F, Prefetch, Value, When
from django.utils.text import capfirst

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_ROW_HEIGHT_RULE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Inches, Mm, Pt

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


COLUMN_WIDTHS = {
    0: Inches(0.597),
    1: Inches(4.106),
    2: Inches(1.279),
    3: Inches(0.69),
    4: Inches(0.59),
    5: Inches(0.886),
    6: Inches(0.59),
    "default": Inches(0.689),
}

HEADER_BG_COLOR = "D9D9D9"


def export(year: int, leerjaar: int) -> Document:
    # complex sorting - year starts around week 33
    toetsen = Toets.objects.filter(jaar=year, klas=leerjaar).order_by("lesweek")
    vakken = Vak.objects.prefetch_related(
        Prefetch("toets_set", queryset=toetsen, to_attr="toetsen")
    )
    return create_document(year, leerjaar, vakken)


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
            toets.tijd or "",
            toets.weging_r4 or "",
        ]

        if weging is not None:
            row.append(getattr(toets, weging[1]) or "")

        assert len(row) == len(header), "Header and row columns mismatch"
        rows.append(row)

    return [header] + rows


def create_document(year: int, leerjaar: int, vakken: Iterable[Vak],) -> Document:
    toetsweken = Kalender.objects.get(jaar=year).toetsweken
    weging = LEERJAAR_WEGING.get(leerjaar)
    _leerjaar = Leerjaren.labels[leerjaar]
    school_year = f"{year}-{year + 1}"

    document = Document()

    # set to landscape
    section = document.sections[-1]
    section.orientation = WD_ORIENT.LANDSCAPE
    # A4 page size
    section.page_width = Mm(297)
    section.page_height = Mm(210)

    # add the document title
    document.add_heading(f"PTAs {_leerjaar} {year}", level=0)

    for vak in vakken:
        header = f"PTA\t{capfirst(vak.naam)}\t{_leerjaar}\t{school_year}"
        document.add_heading("", level=1).add_run(header).bold = True

        [header, *rows] = get_toets_table(vak, toetsweken, weging)

        table = document.add_table(rows=len(rows) + 1, cols=len(header))
        table.style = "TableGrid"
        table.autofit = False

        header_cells = table.rows[0].cells
        for index, title in enumerate(header):
            cell = header_cells[index]
            cell.text = title
            _make_bold(cell)
            _set_cell_bg(cell)

        for index, row in enumerate(rows, 1):
            row_cells = table.rows[index].cells
            for _index, content in enumerate(row):
                row_cells[_index].text = str(content)

        # style the cells: widths, font
        for row in table.rows:
            _make_bold(row.cells[0])
            for index, cell in enumerate(row.cells):
                center = index != 1
                _style_cell(cell, center=center)

        for index, column in enumerate(table.columns):
            column.width = COLUMN_WIDTHS.get(index, COLUMN_WIDTHS["default"])

        for row in table.rows:
            row.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST
            row.height = Inches(0.276)

        document.add_page_break()

    return document


def _make_bold(cell):
    cell.paragraphs[0].runs[0].font.bold = True


def _style_cell(cell, center=True):
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

    for paragraph in cell.paragraphs:
        if center:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

        for run in paragraph.runs:
            run.font.name = "Arial"
            run.font.size = Pt(10)


def _set_cell_bg(cell, color: str = HEADER_BG_COLOR):
    shading_elm_1 = parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls("w"), color))
    cell._tc.get_or_add_tcPr().append(shading_elm_1)
