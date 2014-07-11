from django.conf.urls import patterns
from django.contrib import admin
from django.contrib import messages
from django import forms
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from bioservices import ChEMBLdb

from compounds.resource import CompoundResource
from mps.base.admin import LockableAdmin
from compounds.models import Compound


class CompoundAdmin(LockableAdmin):
    resource_class = CompoundResource

    class Media(object):
        js = ('compounds/customize_admin.js',)

    class AddMultiForm(forms.Form):

        chemblids = forms.CharField(required=True, label="ChEMBL IDs",
                                    widget=forms.Textarea(),
                                    help_text="<br>ChEMBL IDs separated by a "
                                              "space or a new line.")

    save_on_top = True
    list_per_page = 300
    list_display = ('name', 'chembl_link', 'known_drug',
                    'molecular_formula', 'last_update', 'locked')
    search_fields = ['=name', 'synonyms', '=chemblid']
    readonly_fields = ('last_update', 'created_by', 'created_on',
                       'modified_by', 'modified_on', 'image_display')
    actions = ['update_fields']

    def image_display(self, obj):
        if obj.chemblid:
            url = (u'https://www.ebi.ac.uk/chembldb/compound/'
                    'displayimage/' + obj.chemblid)
            return '<img src="%s">' % \
                url
        return ''

    image_display.allow_tags = True
    image_display.short_description = 'Image'

    fieldsets = (
        (None, {
            'fields': (('name', 'image_display'),
                       'chemblid', 'inchikey', 'last_update',)
        }),
        ('Molecular Identifiers', {
            'fields': ('smiles', 'synonyms')
        }),
        ('Molecular Properties', {
            'fields': ('molecular_formula', 'molecular_weight',
                       'rotatable_bonds',
                       'acidic_pka', 'basic_pka',
                       'logp', 'logd', 'alogp',)
        }),
        ('Drug(-like) Properties', {
            'fields': ('known_drug', 'medchem_friendly', 'ro3_passes',
                       'ro5_violations', 'species',)
        }),
        ('Change Tracking', {
            'fields': (
                'locked',
                ('created_by', 'created_on'),
                ('modified_by', 'modified_on'),
                ('signed_off_by', 'signed_off_date'),
            )
        }
        ),
    )

    def get_urls(self):

        return patterns('',
                        (r'^add_multi/$',
                         self.admin_site.admin_view(self.add_compounds))
        ) + super(CompoundAdmin, self).get_urls()

    def add_compounds(self, request):

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
                    if Compound.objects.filter(chemblid=chemblid):
                        skipped += 1
                        continue
                    try:
                        data = ChEMBLdb().get_compounds_by_chemblId(
                            str(chemblid)
                        )
                    except Exception:
                        notfound += 1
                    else:
                        if data:
                            counter += 1
                            data['locked'] = True
                            Compound.objects.create(**data)

                if counter:
                    self.message_user(request,
                                      "Successfully added {} compound{}."
                                      .format(counter,
                                              '' if counter == 1 else 's'))
                if skipped:
                    self.message_user(request, "Skipped {} compound{} that "
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

        return render_to_response('compounds/add_multi.html', {
            'title': 'Add multiple compounds',
            'opts': self.model._meta,
            'form': form,
            # 'root_path': self.admin_site.root_path,
        }, context_instance=RequestContext(request))


admin.site.register(Compound, CompoundAdmin)
