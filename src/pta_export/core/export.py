import html
import logging
from typing import Dict, Iterable, List, Optional, Tuple

from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.models import Prefetch
from django.db.models.functions import Lower
from django.utils.text import capfirst, normalize_newlines

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_ROW_HEIGHT_RULE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Cm, Mm, Pt

from .constants import Leerjaren
from .models import Kalender, Toets, Vak, Voetnoot
from .utils import get_se_weging

logger = logging.getLogger(__name__)


LEERJAAR_WEGING = {
    Leerjaren.havo_4: ("Weging ED4", "weging_ed4"),
    Leerjaren.vwo_4: ("Weging ED4", "weging_ed4"),
    Leerjaren.havo_5: ("Weging ED5", "weging_ed5"),
    Leerjaren.vwo_5: ("Weging ED5", "weging_ed5"),
    Leerjaren.vwo_6: ("Weging ED6", "weging_ed6"),
}

SE_WEGING = {
    Leerjaren.havo_5: True,
    Leerjaren.vwo_6: True,
}

COLUMN_WIDTHS = {
    0: Cm(1.51),
    1: Cm(10.43),
    2: Cm(3.25),
    3: Cm(1.75),
    4: Cm(1.5),
    5: Cm(2.25),
    6: Cm(1.5),
}

HEADER_BG_COLOR = "D9D9D9"


def export(year: int, leerjaar: int) -> Document:
    toetsen = Toets.objects.filter(jaar=year, klas=leerjaar).order_by("lesweek")
    voetnoten = Voetnoot.objects.order_by("id")

    vakken = Vak.objects.prefetch_related(
        Prefetch("toets_set", queryset=toetsen, to_attr="toetsen"),
        Prefetch("voetnoot_set", queryset=voetnoten, to_attr="voetnoten"),
    ).order_by(Lower("naam"))
    return create_document(year, leerjaar, vakken)


def get_toets_table(
    vak: Vak,
    toetsweek_periodes: Dict[int, List[int]],
    toetsweken: List[int],
    weging: Optional[Tuple[str, str]],
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
        week = toets.week or ""

        if toets.week in toetsweken:
            periode = f"{periode} (tw)"
            week = "/".join([str(wk) for wk in toetsweek_periodes[toets.periode]])

        omschrijving = html.unescape(normalize_newlines(toets.omschrijving).strip())
        voetnoot = toets.voetnoot or ""

        row = [
            toets.code,
            (omschrijving, voetnoot),
            toets.domein,
            periode,
            week,
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
    toetsweek_periodes = Kalender.objects.get(jaar=year).toetsweek_periodes
    toetsweken = sum(toetsweek_periodes.values(), [])
    weging = LEERJAAR_WEGING.get(leerjaar)
    _leerjaar = Leerjaren.labels[leerjaar]
    school_year = f"{year}-{year + 1}"
    logo_path = staticfiles_storage.path("img/logopta.jpg")

    document = Document()

    # set to landscape
    section = document.sections[-1]
    section.orientation = WD_ORIENT.LANDSCAPE
    # A4 page size
    section.page_width = Mm(297)
    section.page_height = Mm(210)
    # set correct margins
    section.bottom_margin = Cm(2.5)
    section.top_margin = Cm(2.5)
    section.left_margin = Cm(2)
    section.right_margin = Cm(2)

    for vak in vakken:
        if not vak.toetsen:
            continue

        # set up the table header
        header_p = document.add_paragraph()
        header_tab_stops = header_p.paragraph_format.tab_stops
        header_tab_stops.add_tab_stop(Cm(3))
        header_tab_stops.add_tab_stop(Cm(16), alignment=WD_TAB_ALIGNMENT.RIGHT)
        header_tab_stops.add_tab_stop(Cm(17.25))

        header_run = header_p.add_run(
            f"PTA\t{capfirst(vak.naam)}\t{_leerjaar}\t{school_year}"
        )
        header_run.font.name = "Arial"
        header_run.font.size = Pt(14)
        header_run.bold = True

        # add the logo
        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        paragraph.add_run().add_picture(logo_path, width=Cm(5.68))

        [header, *rows] = get_toets_table(vak, toetsweek_periodes, toetsweken, weging)

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
                center = _index != 1

                cell = row_cells[_index]
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

                if isinstance(content, tuple):
                    content, extra = content
                else:
                    extra = ""

                par = cell.paragraphs[0]
                if center:
                    par.alignment = WD_ALIGN_PARAGRAPH.CENTER

                run = par.add_run(text=str(content))
                run.font.name = "Arial"
                run.font.size = Pt(10)
                if _index == 0:
                    run.bold = True

                if extra:
                    extra_par = cell.add_paragraph()
                    extra_run = extra_par.add_run(text=f"{extra}")
                    extra_run.font.name = "Arial"
                    extra_run.font.size = Pt(9)
                    extra_run.italic = True

        # style the cells: widths, font
        for row in table.rows:
            for index, cell in enumerate(row.cells):
                center = index != 1
                _style_cell(cell, center=center)

        # set the column widths
        num_extra_columns = len(table.columns) - len(COLUMN_WIDTHS)
        remaining_width = (
            section.page_width
            - section.left_margin
            - section.right_margin
            - sum(COLUMN_WIDTHS.values())
            - Mm(1)
        )
        extra_column_width = int(remaining_width / num_extra_columns)
        for index, column in enumerate(table.columns):
            column.width = COLUMN_WIDTHS.get(index, extra_column_width)
            # sigh... dumb format
            for cell in column.cells:
                cell.width = column.width

        for row in table.rows:
            row.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST
            row.height = Cm(0.7)

        # add note for se_weging
        se_weging = get_se_weging(year, leerjaar, vak)
        if se_weging is not None:
            denumerator, *numerators = se_weging

            bits = []
            for numerator, label in zip(numerators, ("ED4", "ED5", "ED6")):
                if not numerator:
                    continue
                bits.append(f"{numerator / denumerator:.01%} {label}")
            full_text = f"Weging eindcijfer: {', '.join(bits)}"
            p_weging = document.add_paragraph(full_text)
            p_weging.paragraph_format.space_before = Pt(10)
            p_weging.style.font.name = "Arial"
            p_weging.style.font.size = Pt(10)

        if vak.voetnoten:
            voetnoten = document.add_paragraph("opmerking\n")
            voetnoten.runs[0].bold = True
            voetnoten.paragraph_format.space_before = Pt(10)
            voetnoten.style.font.bold = False
            voetnoten.style.font.name = "Arial"
            voetnoten.style.font.size = Pt(10)

            for voetnoot in vak.voetnoten:
                _voetnoot = normalize_newlines(voetnoot.noot)
                voetnoten.add_run(f"{_voetnoot}\n")

        document.add_page_break()

    return document


def _make_bold(cell):
    cell.paragraphs[0].runs[0].bold = True


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
