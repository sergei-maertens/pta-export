from django.test import SimpleTestCase

from freezegun import freeze_time

from ..constants import Leerjaren
from ..models import Toets, Vak
from ..utils import get_se_weging


@freeze_time("2020-07-21T08:54:00")
class SEWegingTests(SimpleTestCase):

    def test_vak_havo_4(self):
        # havo 4 is not expected to have any aspect of year 5 or 6
        vak = Vak(naam="Scheikunde")
        vak.toetsen = [
            Toets(
                jaar=2019,
                klas=Leerjaren.havo_4,
                vak=vak,
                pct=40,
            ),
        ]

        weging = get_se_weging(2019, Leerjaren.havo_4, vak)

        self.assertIsNone(weging)

    def test_vak_vwo_4(self):
        # havo 4 is not expected to have any aspect of year 5 or 6
        vak = Vak(naam="Scheikunde")
        vak.toetsen = [
            Toets(
                jaar=2019,
                klas=Leerjaren.vwo_4,
                vak=vak,
                pct=40,
            ),
        ]

        weging = get_se_weging(2019, Leerjaren.havo_5, vak)

        self.assertIsNone(weging)

    def test_vak_havo_5(self):
        vak = Vak(naam="Scheikunde")
        vak.toetsen = [
            Toets(
                jaar=2019,
                klas=Leerjaren.havo_5,
                vak=vak,
                pct=0,
            ),
        ]
        Toets.objects.create(vak=vak, klas=Leerjaren.havo_4, pct=40, jaar=2018)

        weging = get_se_weging(2019, Leerjaren.havo_5, vak)

        self.assertEqual(weging, (5, 2, 3, 0))

    def test_vak_vwo_5(self):
        pass
