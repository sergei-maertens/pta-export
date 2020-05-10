from django.core.management import BaseCommand, CommandError

from ...constants import Leerjaren
from ...export import export


class Command(BaseCommand):
    help = "Export PTAs for a given year and klas"

    @staticmethod
    def add_arguments(parser):
        parser.add_argument("year", type=int, help="Year to export")
        parser.add_argument("klas", type=int, help="ID of the leerjaar")

    def handle(self, **options):
        klas = options["klas"]
        if klas not in Leerjaren:
            raise CommandError("Invalid Leerjaar ID given")

        export(options["year"], klas)
