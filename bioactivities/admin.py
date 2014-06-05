from django.conf.urls import patterns
from django.contrib import admin
from django.contrib import messages
from django import forms
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.forms import Textarea

from bioactivities.resource import BioactivityTypeResource
from mps.base.admin import LockableAdmin
from .models import *


class TargetAdmin(LockableAdmin):
    class Media(object):
        js = ('bioactivities/customize_admin.js',)

    class AddMultiForm(forms.Form):

        chemblids = forms.CharField(
            required=True,
            label="ChEMBL IDs",
            widget=forms.Textarea(),
            help_text="<br>ChEMBL IDs separated by a space or a new line."
        )

    save_on_top = True
    list_per_page = 20
    list_display = ('name', 'organism', 'target_type', 'chembl_link', 'locked')
    search_fields = ['name', 'organism', 'synonyms', '=chemblid']
    actions = ['update_fields']
    readonly_fields = ('last_update', )

    def get_urls(self):

        return patterns('',
                        (r'^add_multi/$',
                         self.admin_site.admin_view(self.add_targets))
        ) + super(TargetAdmin, self).get_urls()

    def add_targets(self, request):

        if '_add' in request.POST:
            form = self.AddMultiForm(request.POST)
            if form.is_valid():
                chemblids = form.cleaned_data['chemblids']
                counter = skipped = invalid = notfound = 0
                chemblids = chemblids.split()
                for chemblid in chemblids:
                    if not chemblid.startswith('CHEMBL'):
                        invalid += 1
                        continue
                    if Target.objects.filter(chemblid=chemblid):
                        skipped += 1
                        continue
                    try:
                        data = chembl_target(chemblid)
                    except Exception:
                        notfound += 1
                    else:
                        if data:
                            data['locked'] = True
                            counter += 1
                            Target.objects.create(**data)

                if counter:
                    self.message_user(request,
                                      "Successfully added {} target{}."
                                      .format(counter,
                                              '' if counter == 1 else 's'))
                if skipped:
                    self.message_user(request, "Skipped {} target{} that "
                                               "{} already in the database."
                                      .format(skipped,
                                              '' if skipped == 1 else 's',
                                              'is' if skipped == 1 else 'are'),
                                      level=messages.WARNING)
                if invalid:
                    self.message_user(request, "Skipped {} invalid "
                                               "identifier{}."
                                      .format(invalid,
                                              '' if invalid == 1 else 's'),
                                      level=messages.WARNING)
                if notfound:
                    self.message_user(request,
                                      "Could not find {} identifier{} in "
                                      "ChEMBL database."
                                      .format(notfound,
                                              '' if notfound == 1 else 's'),
                                      level=messages.WARNING)

                return HttpResponseRedirect(request.get_full_path())
        else:
            form = self.AddMultiForm()

        return render_to_response('bioactivities/add_multi.html', {
            'title': 'Add multiple targets',
            'opts': self.model._meta,
            'form': form,
            'what': 'target',
            # 'root_path': self.admin_site.root_path,
        }, context_instance=RequestContext(request))


admin.site.register(Target, TargetAdmin)


class AssayAdmin(LockableAdmin):
    class Media(object):
        js = ('bioactivities/customize_admin.js',)

    class AddMultiForm(forms.Form):

        chemblids = forms.CharField(required=True, label="ChEMBL IDs",
                                    widget=forms.Textarea(),
                                    help_text="<br>ChEMBL IDs separated by a "
                                              "space or a new line.")

    save_on_top = True
    list_per_page = 20
    list_display = (
        'description', 'chembl_link', 'organism', 'assay_type', 'locked')
    search_fields = ['description', '=chemblid']
    actions = ['update_fields']

    readonly_fields = ('last_update', )
    fields = ('chemblid', 'description', 'assay_type', 'organism', 'strain',
              'journal', 'locked')

    def get_urls(self):

        return patterns('',
                        (r'^add_multi/$',
                         self.admin_site.admin_view(self.add_assays))
        ) + super(AssayAdmin, self).get_urls()

    def add_assays(self, request):

        if '_add' in request.POST:
            form = self.AddMultiForm(request.POST)
            if form.is_valid():
                chemblids = form.cleaned_data['chemblids']
                counter = skipped = invalid = notfound = 0
                chemblids = chemblids.split()
                for chemblid in chemblids:
                    if not chemblid.startswith('CHEMBL'):
                        invalid += 1
                        continue
                    if Assay.objects.filter(chemblid=chemblid):
                        skipped += 1
                        continue
                    try:
                        data = chembl_assay(chemblid)
                    except Exception:
                        notfound += 1
                    else:
                        if data:
                            data['locked'] = True
                            counter += 1
                            Assay.objects.create(**data)

                if counter:
                    self.message_user(request,
                                      "Successfully added {} assay{}."
                                      .format(counter,
                                              '' if counter == 1 else 's'))
                if skipped:
                    self.message_user(request, "Skipped {} assay{} that "
                                               "{} already in the database."
                                      .format(skipped,
                                              '' if skipped == 1 else 's',
                                              'is' if skipped == 1 else 'are'),
                                      level=messages.WARNING)
                if invalid:
                    self.message_user(request, "Skipped {} invalid "
                                               "identifier{}."
                                      .format(invalid,
                                              '' if invalid == 1 else 's'),
                                      level=messages.WARNING)
                if notfound:
                    self.message_user(request,
                                      "Could not find {} identifier{} in "
                                      "ChEMBL database."
                                      .format(notfound,
                                              '' if notfound == 1 else 's'),
                                      level=messages.WARNING)

                return HttpResponseRedirect(request.get_full_path())
        else:
            form = self.AddMultiForm()

        return render_to_response('bioactivities/add_multi.html', {
            'title': 'Add multiple assays',
            'opts': self.model._meta,
            'form': form,
            'what': 'assay',
            # 'root_path': self.admin_site.root_path,
        }, context_instance=RequestContext(request))


admin.site.register(Assay, AssayAdmin)


class BioactivityAdmin(LockableAdmin):
    save_on_top = True
    list_per_page = 20
    raw_id_fields = ("compound",)

    def chembl_link(self, obj):
        return obj.assay.chembl_link()

    chembl_link.allow_tags = True
    chembl_link.short_description = 'CHEMBL Links'

    list_display = (
        'compound',
        'chembl_link',
        'bioactivity_type',
        'standard_name',
        'operator',
        'locked',
        'standardized_value',
        'standardized_units',
        'value',
        'units'
    )
    search_fields = ['compound__name', 'target__name', 'bioactivity_type']
    actions = ['update_fields']

    fieldsets = (
        (None, {
            'fields': (('compound', 'assay'), ('target', 'target_confidence'),
                       ('bioactivity_type', 'value', 'units'),
                       ('standard_name', 'standardized_value', 'standardized_units'),
                       ('activity_comment', 'reference', 'name_in_reference'), 'locked',
                       ('created_by', 'created_on'), ('modified_by', 'modified_on'),
                       ('signed_off_by', 'signed_off_date'),)
        }),
    )

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 20})}
    }


admin.site.register(Bioactivity, BioactivityAdmin)


class BioactivityTypeAdmin(LockableAdmin):
    resource_class = BioactivityTypeResource
    save_on_top = True
    list_per_page = 20
    list_display = (
        'chembl_bioactivity',
        'standard_name',
        'description',
        'standard_unit',
    )
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 30})}
    }


admin.site.register(BioactivityType, BioactivityTypeAdmin)
