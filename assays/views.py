from django.views.generic import ListView
from assays.models import AssayRun

class RunList(ListView):
    model = AssayRun
