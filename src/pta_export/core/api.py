from django.urls import path

from rest_framework import permissions, serializers
from rest_framework.generics import CreateAPIView

from .constants import Leerjaren
from .models import Kalender
from .views import get_export_response


class ExportSerializer(serializers.Serializer):
    jaar = serializers.IntegerField(
        label="Jaar", required=True, help_text="Jaar in YYYY formaat, bv. 2019."
    )
    klas = serializers.ChoiceField(
        label="klas", choices=[choice for choice in Leerjaren.choices if choice[0]],
    )

    def validate_jaar(self, value: int):
        if not Kalender.objects.filter(jaar=value).exists():
            raise serializers.ValidationError("Er bestaat geen kalendar voor dit jaar.")
        return value


class ExportAPIView(CreateAPIView):
    """
    Create an export.

    This endpoint requires authorization. You must either be logged in, or send the
    `Authorization` HTTP header with a valid token:

        Authorization: Token abcdefghij

    Required parameters:

    - `jaar`: year in the YYYY format, e.g. 2019
    - `klas`: Array index of the klas/leerjaar, e.g. `1` for "4 havo"

    The response is a file response, containing the file as attachment.
    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ExportSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        jaar = serializer.validated_data["jaar"]
        leerjaar = serializer.validated_data["klas"]
        return get_export_response(jaar, leerjaar)


urlpatterns = [
    path("export", ExportAPIView.as_view(), name="export"),
]
