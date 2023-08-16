import math
from typing import Optional, Tuple

from .constants import Breuken, Leerjaren
from .models import Toets, Vak

YEAR_4 = (Leerjaren.havo_4, Leerjaren.vwo_4)
YEAR_5 = (Leerjaren.havo_5, Leerjaren.vwo_5)
YEAR_6 = (Leerjaren.vwo_6,)

HAVO = (Leerjaren.havo_4, Leerjaren.havo_5)
VWO = (Leerjaren.vwo_3, Leerjaren.vwo_4, Leerjaren.vwo_5, Leerjaren.vwo_6)

OVERSTAPPERS = (Leerjaren.overstappers_vwo_5, Leerjaren.overstappers_vwo_6)

SIMPLE_WEGING = {
    Leerjaren.vwo_3: "ED4",
    Leerjaren.vwo_4: "ED4",
    Leerjaren.havo_4: "ED4",
    Leerjaren.vwo_5: "ED5",
}


def get_previous_leerjaar(leerjaar: int) -> int:
    # determine the previous leerjaar
    if leerjaar in HAVO:
        container = HAVO
    elif leerjaar in VWO:
        container = VWO
    else:
        raise ValueError(f"Unknown container for leerjaar {leerjaar}")

    idx = container.index(leerjaar)
    return container[idx - 1]


def get_se_weging(
    year: int, leerjaar: int, vak: Vak
) -> Optional[Tuple[int, int, int, int]]:
    """
    Determine the "SE-weging".

    SE-Weging is "schoolexamenweging". It takes into account previous years portion in
    the total result. For a Vak in year 5, year 4 can be relevant. For a Vak in year
    6, year 4 and/or 5 can be relevant.

    Wegingen can be specified in percentages or in exact divisions. :func:`parse_edx`
    is used to reduce everything to an exact division.

    The relevant formula is::

        (a * ED4 + b * ED5 + c * ED6) / (a + b + c)

    """
    assert hasattr(vak, "toetsen"), "Toetsen must be prefetched"
    assert all(
        toets.jaar == year for toets in vak.toetsen
    ), "All toetsen must be from the same year"

    # year 4 -> 100% ED4, nothing to calculate
    if leerjaar in YEAR_4:
        return None

    if leerjaar in OVERSTAPPERS:
        return None

    toets_this_year: Optional[Toets] = vak.toets_set.filter(
        jaar=year, klas=leerjaar
    ).first()
    if not toets_this_year:
        return None

    # works for both HAVO and VWO
    previous_leerjaar = get_previous_leerjaar(leerjaar)

    # fetch a Toets from the previous year
    toets_one_year_ago: Optional[Toets] = vak.toets_set.filter(
        jaar=year - 1, klas=previous_leerjaar
    ).first()

    if leerjaar in YEAR_6:
        two_leerjaren_ago = get_previous_leerjaar(previous_leerjaar)
        toets_two_years_ago = vak.toets_set.filter(
            jaar=year - 2, klas=two_leerjaren_ago
        ).first()
        toets_ed4 = toets_two_years_ago
        toets_ed5 = toets_one_year_ago
    else:
        toets_ed4 = toets_one_year_ago
        toets_ed5 = toets_this_year

    if toets_ed4 is None:
        return None
    assert isinstance(toets_ed4, Toets)

    numerator_ed4, denumerator_ed4 = parse_edx(toets_ed4.pct or 0)
    numerator_ed5, denumerator_ed5 = parse_edx((toets_ed5.pct or 0) if toets_ed5 else 0)

    denumerator = denumerator_ed4 * denumerator_ed5

    numerator_4 = denumerator_ed5 * numerator_ed4

    if leerjaar in HAVO:
        numerator_5 = denumerator - numerator_4
        numerator_6 = 0
        gcd = math.gcd(numerator_4, numerator_5)
    elif leerjaar in VWO:
        numerator_5 = denumerator_ed4 * numerator_ed5
        numerator_6 = denumerator - numerator_4 - numerator_5
        gcd = math.gcd(math.gcd(numerator_4, numerator_5), numerator_6)
    else:
        raise RuntimeError(f"Unknown leerjaar: {leerjaar}")

    # reduce back to the smallest numbers using the GCD
    denumerator /= gcd
    numerator_4 /= gcd
    numerator_5 /= gcd
    numerator_6 /= gcd  # either zero or used as input for the gcd derivation

    if denumerator == 1:
        return None

    return (
        int(denumerator),
        int(numerator_4),
        int(numerator_5),
        int(numerator_6),
    )


def parse_edx(edx: int) -> Tuple[int, int]:
    """
    Figure out the numerator/denumerator for a particular "weging".

    If the weging is between 0-100, then it's a straight up percentage. If it exceeds
    100, the number after 100 indicates the 'index' in the Breuken choices for an
    exact representation.

    :return: Tuple of integers - (numerator, denumerator)
    """
    if edx == 0:
        return (0, 1)

    if 1 <= edx <= 100:
        return (edx, 100)

    if edx > 100:
        choice_index = edx - 100  # 103 -> index 3 in choices
        label = Breuken.labels[choice_index]  # format t/n
        bits = [int(x) for x in label.split("/")]
        assert len(bits) == 2
        return tuple(bits)

    raise ValueError("Value must be positive")


def get_simple_weging(vak: Vak) -> Optional[str]:
    if not vak.toetsen:
        return None

    pct = vak.toetsen[0].pct
    if not pct:
        return None

    if 1 <= pct <= 100:
        return f"{pct}%"

    if pct > 100:
        choice_index = pct - 100  # 103 -> index 3 in choices
        label = Breuken.labels[choice_index]  # format t/n
        return label

    raise ValueError("Value must be positive")


def get_weging_text(year: int, leerjaar: int, vak: Vak) -> Optional[str]:
    if leerjaar in SIMPLE_WEGING:
        return None

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
        return f"berekening SE cijfer: {_weging}"

    return None
