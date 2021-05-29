from io import BytesIO

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse
from django.views.generic import FormView

from .constants import Leerjaren
from .export import export
from .forms import ExportForm


def get_export_response(jaar: int, leerjaar: int):
    _leerjaar = dict(Leerjaren.choices)[leerjaar]

    document = export(jaar, leerjaar)

    outfile = BytesIO()
    document.save(outfile)
    outfile.seek(0)

    response = FileResponse(
        outfile,
        as_attachment=True,
        filename=f"{jaar}-{_leerjaar}.docx",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    return response


class ExportView(LoginRequiredMixin, FormView):
    form_class = ExportForm
    template_name = "export.html"

    def form_valid(self, form: ExportForm):
        jaar = form.cleaned_data["jaar"]
        leerjaar = form.cleaned_data["klas"]
        return get_export_response(jaar, leerjaar)
