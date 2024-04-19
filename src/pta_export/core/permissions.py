from collections.abc import Sequence

from .constants import AccessModes, Leerjaren, Sectoren
from .models import User as PtaUser


def get_allowed_leerjaren(pta_user: PtaUser | None) -> Sequence[Leerjaren]:
    if pta_user is None:
        return []

    if pta_user.access == AccessModes.export_any:
        return [choice for choice in Leerjaren if choice.value]

    if pta_user.access == AccessModes.export_by_sector:

        match pta_user.sector:
            case Sectoren.onderbouw:
                return Leerjaren.get_onderbouw_havo_vwo()
            case Sectoren.bovenbouw:
                return Leerjaren.get_bovenbouw_havo_vwo()
            case Sectoren.vmbo:
                return Leerjaren.get_vmbo()
            case _:
                return []

    return []
