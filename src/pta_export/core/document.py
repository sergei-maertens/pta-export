import html
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from django.template.defaultfilters import date as format_date
from django.utils.text import capfirst, normalize_newlines

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_ROW_HEIGHT_RULE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Cm, Mm, Pt

from .constants import Leerjaren
from .models import Vak
from .utils import get_se_weging, get_simple_weging

LEERJAAR_WEGING = {
    Leerjaren.havo_4: ("Weging ED4", "weging_ed4"),
    Leerjaren.vwo_4: ("Weging ED4", "weging_ed4"),
    Leerjaren.havo_5: ("Weging ED5", "weging_ed5"),
    Leerjaren.vwo_5: ("Weging ED5", "weging_ed5"),
    Leerjaren.vwo_6: ("Weging ED6", "weging_ed6"),
}


R4_LEERJAREN = (
    Leerjaren.vwo_4,
    Leerjaren.vwo_5,
    Leerjaren.havo_4,
)

HEADER_BG_COLOR = "D9D9D9"

SIMPLE_WEGING = {
    Leerjaren.vwo_4: "ED4",
    Leerjaren.havo_4: "ED4",
    Leerjaren.vwo_5: "ED5",
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


def initialize_document() -> Document:
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

    return document


def add_vak(
    document: Document,
    logo_path: str,
    vak: Vak,
    year: int,
    leerjaar: int,
    toetsweek_periodes: Dict[int, List[int]],
):
    if leerjaar not in (Leerjaren.overstappers_vwo_5, Leerjaren.overstappers_vwo_6):
        add_vak_regular(document, logo_path, vak, year, leerjaar, toetsweek_periodes)
    elif leerjaar == Leerjaren.overstappers_vwo_5:
        add_vak_overstappers_vwo5(document, logo_path, vak, year, leerjaar)


@dataclass
class Omschrijving:
    content: str
    inleverdatum: str
    voetnoot: str

    _voetnoot_counter = 0
    voetnoot_nr = 0

    def __post_init__(self):
        if self.voetnoot:
            self.__class__._voetnoot_counter += 1
            self.voetnoot_nr = self.__class__._voetnoot_counter

    @classmethod
    def reset_counter(cls):
        cls._voetnoot_counter = 0


def clean_text(text: str) -> str:
    return html.unescape(normalize_newlines(text).strip())


def get_toets_table(
    leerjaar: int,
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
        "Tijd\n(min)",
    ]

    if leerjaar in R4_LEERJAREN:
        header.append("Weging R4")

    if weging is not None:
        header.append(weging[0])

    rows = []

    for toets in vak.toetsen:
        periode = toets.periode
        week = toets.week or ""

        if toets.week in toetsweken:
            periode = f"{periode} (tw)"
            week = "/".join([str(wk) for wk in toetsweek_periodes[toets.periode]])

        if toets.inleverdatum:
            formatted = format_date(toets.inleverdatum, "j F Y")
            inleverdatum = f"inleverdatum: {formatted}"
        elif toets.datum:
            formatted = format_date(toets.datum, "j F Y")
            inleverdatum = f"datum: {formatted}"
        else:
            inleverdatum = ""

        soort_werk = (
            toets.soortwerk.naam if toets.soortwerk and toets.soortwerk.id != 12 else ""
        )
        row = [
            toets.code,
            Omschrijving(
                content=clean_text(toets.omschrijving),
                inleverdatum=inleverdatum,
                voetnoot=toets.voetnoot,
            ),
            toets.domein or "",
            periode or "",
            week,
            soort_werk,
            toets.tijd or "",
        ]

        if leerjaar in R4_LEERJAREN:
            row.append(toets.weging_r4 or "")

        if weging is not None:
            row.append(getattr(toets, weging[1]) or "")

        assert len(row) == len(header), "Header and row columns mismatch"
        rows.append(row)

    return [header] + rows


def add_header(document: Document, vak: Vak, year: int, leerjaar: int):
    _leerjaar = Leerjaren.labels[leerjaar]
    school_year = f"{year}-{year + 1}"

    # set up the table header
    header_p = document.add_paragraph()
    header_tab_stops = header_p.paragraph_format.tab_stops
    header_tab_stops.add_tab_stop(Cm(3))
    header_tab_stops.add_tab_stop(Cm(16), alignment=WD_TAB_ALIGNMENT.RIGHT)
    header_tab_stops.add_tab_stop(Cm(17.25))

    vak_naam = capfirst(html.unescape(vak.naam))
    if vak.afkorting and vak.weergeven == 1:
        vak_naam = f"{vak_naam} ({vak.afkorting})"

    header_run = header_p.add_run(f"PTA\t{vak_naam}\t{_leerjaar}\t{school_year}")
    # header_run.font.name = "Arial"
    header_run.font.size = Pt(14)
    header_run.bold = True


def add_vak_regular(
    document: Document,
    logo_path: str,
    vak: Vak,
    year: int,
    leerjaar: int,
    toetsweek_periodes: Dict[int, List[int]],
):
    if not vak.toetsen:
        return

    section = document.sections[-1]

    toetsweken = sum(toetsweek_periodes.values(), [])
    weging = LEERJAAR_WEGING.get(leerjaar)

    add_header(document, vak, year, leerjaar)

    # add the logo
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    # paragraph.add_run().add_picture(logo_path, width=Cm(5.68))

    # try to set global font name
    _set_default_font(paragraph)

    Omschrijving.reset_counter()
    [header, *rows] = get_toets_table(
        leerjaar, vak, toetsweek_periodes, toetsweken, weging
    )

    table = document.add_table(rows=len(rows) + 1, cols=len(header))
    _set_default_table_style(table)

    header_cells = table.rows[0].cells
    for index, title in enumerate(header):
        cell = header_cells[index]
        cell.text = title
        cell.paragraphs[0].runs[0].bold = True
        _set_cell_bg(cell)

    toets_content = []

    for index, row in enumerate(rows, 1):
        row_cells = table.rows[index].cells
        for _index, content in enumerate(row):
            cell = row_cells[_index]
            par = cell.paragraphs[0]

            # normal content
            if not isinstance(content, Omschrijving):
                par.text = str(content)
            # calculated content
            else:
                toets_content.append(content)
                par.add_run(text=content.content)

                if content.voetnoot:
                    par.add_run(text=" ")
                    voetnoot_run = par.add_run(text=f"{content.voetnoot_nr})")
                    voetnoot_run.font.superscript = True

                if content.inleverdatum:
                    datum_par = cell.add_paragraph(text=content.inleverdatum)
                    datum_par.runs[0].font.size = Pt(9)
                    datum_par.runs[0].italic = True
    _style_table_cells(table)

    # set the column widths
    num_extra_columns = len(table.columns) - len(COLUMN_WIDTHS)
    remaining_width = (
        section.page_width
        - section.left_margin
        - section.right_margin
        - sum(COLUMN_WIDTHS.values())
        - Mm(1)
    )
    extra_column_width = (
        int(remaining_width / num_extra_columns) if num_extra_columns else 0
    )
    for index, column in enumerate(table.columns):
        column.width = COLUMN_WIDTHS.get(index, extra_column_width)
        # sigh... dumb format
        for cell in column.cells:
            cell.width = column.width

    weging_text = None
    if leerjaar in SIMPLE_WEGING:
        se_weging = get_simple_weging(vak)
        if se_weging:
            weging_label = SIMPLE_WEGING[leerjaar]
            weging_text = (
                f"* Het {weging_label} cijfer telt {se_weging} mee "
                "in het schoolexamencijfer"
            )
    else:
        # add note for se_weging
        se_weging = get_se_weging(year, leerjaar, vak)
        if se_weging is not None:
            denumerator, *numerators = se_weging

            bits = []
            for numerator, label in zip(numerators, ("ED4", "ED5", "ED6")):
                if not numerator:
                    continue
                bits.append(f"{numerator}x {label}")

            _weging = f"({' + '.join(bits)}) / {denumerator}"
            weging_text = f"berekening SE cijfer: {_weging}"

    if weging_text:
        p_weging = document.add_paragraph(weging_text)
        p_weging.paragraph_format.space_before = Pt(10)
        p_weging.runs[0].font.size = Pt(10)

    toets_voetnoot_content = [x for x in toets_content if x.voetnoot]
    if toets_voetnoot_content:
        p_toets_voetnoten = document.add_paragraph()
        p_toets_voetnoten.paragraph_format.space_before = Pt(10)
        for content in toets_voetnoot_content:
            run_super = p_toets_voetnoten.add_run(text=f"{content.voetnoot_nr})")
            run_super.font.superscript = True
            p_toets_voetnoten.add_run(text=f" {normalize_newlines(content.voetnoot)}\n")

    vak_voetnoten = [voetnoot.noot for voetnoot in vak.voetnoten]
    if vak_voetnoten:
        voetnoten = document.add_paragraph("opmerking\n")
        voetnoten.runs[0].bold = True
        voetnoten.paragraph_format.space_before = Pt(10)

        for voetnoot in vak_voetnoten:
            _voetnoot = normalize_newlines(voetnoot)
            voetnoten.add_run(f"{_voetnoot}\n")

    document.add_page_break()


def add_vak_overstappers_vwo5(
    document: Document, logo_path: str, vak: Vak, year: int, leerjaar: int,
):
    render_vak = any((vak.overnemen_herwaarderen, vak.inhalen, vak.inhaalopdrachten,))
    if not render_vak:
        return

    add_header(document, vak, year, leerjaar)

    if vak.overnemen_herwaarderen:

        paragraph = document.add_paragraph(
            "De volgende al gemaakte onderdelen worden meegenomen uit "
            "eerdere leerjaren.\nDaarbij wordt het cijfer overgenomen, of de "
            "toets wordt opnieuw gewaardeerd."
        )
        # try to set global font name
        _set_default_font(paragraph)

        table = document.add_table(rows=len(vak.overnemen_herwaarderen) + 1, cols=6)
        _set_default_table_style(table)

        # add table header
        header = [
            "Code V4/V5",
            "Jaar",
            "Omschrijving",
            "Domein",
            "Overnemen/Herwaarderen",
            "Weging ED4",
        ]
        _set_table_header(table, header)

        # add table body
        for index, overstap in enumerate(vak.overnemen_herwaarderen, 1):
            jaar = f"{overstap.oude_toets.jaar}-{overstap.oude_toets.jaar + 1}"

            row_cells = table.rows[index].cells
            row_cells[0].text = overstap.oude_toets.code
            row_cells[1].text = jaar
            row_cells[2].text = clean_text(overstap.oude_toets.omschrijving)
            row_cells[3].text = overstap.oude_toets.domein
            row_cells[4].text = overstap.get_actie_display()
            row_cells[5].text = str(overstap.weging_ed4)
        _style_table_cells(table, index_no_center=2)

        # style table dimensions
        WIDTHS = {
            0: Cm(2.00),
            1: Cm(2.50),
            2: Cm(10.43),
            3: Cm(3.25),
            4: Cm(3.00),
            5: Cm(2.00),
        }
        _set_column_widths(table, WIDTHS)

    if vak.inhalen:
        paragraph = document.add_paragraph(
            "De volgende toetsen uit havo 4 moeten worden ingehaald."
        )
        # try to set global font name
        _set_default_font(paragraph)
        if vak.overnemen_herwaarderen:
            paragraph.paragraph_format.space_before = Pt(10)

        table = document.add_table(rows=len(vak.inhalen) + 1, cols=5)
        _set_default_table_style(table)

        # add table header
        header = ["Code H4", "Jaar", "Omschrijving", "Domein", "Weging ED4"]
        _set_table_header(table, header)

        # add table body
        for index, overstap in enumerate(vak.inhalen, 1):
            jaar = f"{overstap.oude_toets.jaar}-{overstap.oude_toets.jaar + 1}"

            row_cells = table.rows[index].cells
            row_cells[0].text = overstap.oude_toets.code
            row_cells[1].text = jaar
            row_cells[2].text = clean_text(overstap.oude_toets.omschrijving)
            row_cells[3].text = overstap.oude_toets.domein
            row_cells[4].text = str(overstap.weging_ed4)
        _style_table_cells(table, index_no_center=2)

        # style table dimensions
        WIDTHS = {
            0: Cm(2.00),
            1: Cm(2.50),
            2: Cm(10.43),
            3: Cm(3.25),
            4: Cm(2.00),
        }
        _set_column_widths(table, WIDTHS)

    if vak.inhaalopdrachten:
        paragraph = document.add_paragraph(
            "Tevens moet de volgende inhaalopdracht worden gemaakt om aan het "
            "schoolexamen Havo te voldoen:"
        )
        # try to set global font name
        _set_default_font(paragraph)
        if vak.overnemen_herwaarderen or vak.inhalen:
            paragraph.paragraph_format.space_before = Pt(10)

        table = document.add_table(rows=len(vak.inhaalopdrachten) + 1, cols=5)
        _set_default_table_style(table)

        # add table header
        header = ["Code H4", "Jaar", "Omschrijving", "Domein", "Weging ED4"]
        _set_table_header(table, header)

        # add table body
        for index, toets in enumerate(vak.inhaalopdrachten, 1):
            jaar = f"{toets.jaar}-{toets.jaar + 1}"

            row_cells = table.rows[index].cells
            row_cells[0].text = toets.code
            row_cells[1].text = jaar
            row_cells[2].text = clean_text(toets.omschrijving)
            row_cells[3].text = toets.domein
            row_cells[4].text = str(toets.weging_ed4)
        _style_table_cells(table, index_no_center=2)

        # style table dimensions
        WIDTHS = {
            0: Cm(2.00),
            1: Cm(2.50),
            2: Cm(10.43),
            3: Cm(3.25),
            4: Cm(2.00),
        }
        _set_column_widths(table, WIDTHS)

    document.add_page_break()


def _set_default_font(paragraph) -> None:
    paragraph.style.font.name = "Arial"
    paragraph.style.font.size = Pt(10)


def _set_default_table_style(table) -> None:
    table.style = "TableGrid"
    table.autofit = False

    for row in table.rows:
        row.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST
        row.height = Cm(0.7)

        for cell in row.cells:
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def _style_table_cells(table, index_no_center=1):
    # style header row
    _set_table_header_style(table.rows[0], index_no_center=index_no_center)

    # style body
    for row in table.rows:
        # style the cells
        for _index, cell in enumerate(row.cells):
            par = cell.paragraphs[0]
            # first column bold
            if _index == 0:
                for run in par.runs:
                    run.font.bold = True
            # center if needed
            if _index != index_no_center:
                for par in cell.paragraphs:
                    par.alignment = WD_ALIGN_PARAGRAPH.CENTER


def _set_table_header(table, header: List[str]) -> None:
    header_cells = table.rows[0].cells
    for index, title in enumerate(header):
        cell = header_cells[index]
        cell.text = title


def _set_table_header_style(header_row, index_no_center=1) -> None:
    for index, cell in enumerate(header_row.cells):
        cell.paragraphs[0].runs[0].bold = True
        if index != index_no_center:
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        _set_cell_bg(cell)


def _set_column_widths(table, widths) -> None:
    for index, column in enumerate(table.columns):
        column.width = widths[index]
        # sigh... dumb format
        for cell in column.cells:
            cell.width = column.width


def _set_cell_bg(cell, color: str = HEADER_BG_COLOR):
    shading_elm_1 = parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls("w"), color))
    cell._tc.get_or_add_tcPr().append(shading_elm_1)
