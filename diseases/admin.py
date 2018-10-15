from django.contrib import admin
from .models import Disease

from mps.base.admin import LockableAdmin


class DiseaseAdmin(LockableAdmin):
    model = Disease

# Register your models here.
admin.site.register(Disease, DiseaseAdmin)
