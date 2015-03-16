from django.contrib import admin
from django.contrib.admin.widgets import AdminURLFieldWidget
from django.db.models import URLField
from django.utils.safestring import mark_safe
from django.forms import Textarea

from mps.base.admin import LockableAdmin
from drugtrials.models import *
from drugtrials.resource import *
from forms import *

from import_export.admin import ImportExportModelAdmin


class URLFieldWidget(AdminURLFieldWidget):
    def render(self, name, value, attrs=None):
        widget = super(URLFieldWidget, self).render(name, value, attrs)

        # u'<input type="button" ' \
        # u'value="Click here to open the URL in a new window." ' \
        # u'style="float: right; clear: both;" ' \
        # u'onclick="window.' \
        # u'open(document.getElementById(\'{1}\')' \
        # u'.value)" />' \

        html = \
            u'<div style="width: 55em; height: 4em;">' \
            u'<div>' \
            u'{0}' \
            u'</div>' \
            u'<div style="float: right; z-index: 10;' \
            u' margin-top: -3em; margin-right: -25em;">' \
            u'<button type="button" onclick="window.open(document.getElementById(\'{1}\').value, \'_newtab\');" ' \
            u'>Open Link in New Tab</button>' \
            u'<button type="button" onclick="window.open(document.getElementById(\'{1}\').value, \'win\', ' \
            u'\'toolbars=0,width=800,height=800,left=200,top=200,scrollbars=1,resizable=1\');" ' \
            u'>Open Link in New Window</button>' \
            u'</div>' \
            u'</div>'.format(widget, attrs['id'])

        return mark_safe(html)


class SpeciesAdmin(LockableAdmin):
    list_per_page = 300
    save_on_top = True
    fieldsets = (
        (
            None, {
                'fields': (
                    'species_name',
                )
            }
        ),
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

admin.site.register(Species, SpeciesAdmin)

# Participants information is now part of DrugTrials model
# instead of a seperate entity


class TrialSourceAdmin(LockableAdmin):
    save_on_top = True
    list_per_page = 300
    list_display = ('source_name', 'source_site', 'description')
    fieldsets = (
        (
            None, {
                'fields': (
                    'source_name',
                    'source_website',
                    'description',
                )
            }
        ),
        (
            'Change Tracking', {
                'fields': (
                    'locked',
                    ('created_by', 'created_on'),
                    ('modified_by', 'modified_on'),
                    ('signed_off_by', 'signed_off_date'),
                )
            }
        ),
    )
    actions = ['update_fields']

    def source_site(self, obj):
        return '<a href="%s" target="_blank">%s</a>' % (obj.source_website, obj.source_website)
    source_site.allow_tags = True

admin.site.register(TrialSource, TrialSourceAdmin)


class FindingResultInline(admin.TabularInline):
    model = FindingResult
    form = FindingResultForm
    raw_id_fields = ('finding_name',)
    verbose_name = 'Organ Finding'
    verbose_name_plural = 'Organ Findings'
    fields = ('finding_name', 'descriptor', 'finding_time', 'time_units',
               'result', 'severity', 'frequency', 'value', 'value_units',)
    extra = 0

    class Media(object):
        css = {"all": ("css/hide_admin_original.css",)}


class DrugTrialAdmin(LockableAdmin):

    form = DrugTrialForm

    class Media(object):
        js = ('js/inline_fix.js',)

    resource_class = DrugTrialResource

    formfield_overrides = {
        URLField: {'widget': URLFieldWidget},
    }

    save_on_top = True
    list_per_page = 300
    list_display = (
        'compound', 'species', 'trial_type', 'trial_sub_type',
        'source_page', 'trial_date', 'locked')
    list_filter = ['trial_type', ]
    search_fields = [
        'compound__name', 'species__species_name']
    actions = ['update_fields']
    raw_id_fields = ('compound',)
    readonly_fields = ['created_on', 'created_by', 'modified_by',
                       'modified_on', 'drug_display', 'figure1_display', 'figure2_display']

    # Display figures
    def figure1_display(self, obj):
        if obj.id and obj.figure1:
            return '<img src="%s">' % \
                   obj.figure1.url
        return ''

    def figure2_display(self, obj):
        if obj.id and obj.figure2:
            return '<img src="%s">' % \
                   obj.figure2.url
        return ''
    figure1_display.allow_tags = True
    figure2_display.allow_tags = True

    def drug_display(self, obj):

        if obj.compound.chemblid:
            url = (u'https://www.ebi.ac.uk/chembldb/compound/'
                   'displayimage/' + obj.compound.chemblid)
            return '<img src="%s">' % \
                url
        else:
            return u''

    drug_display.allow_tags = True
    drug_display.short_description = 'Structure'

    fieldsets = (
        (None, {
            'fields': (('compound', 'title'),
                       ('drug_display', 'figure1_display', 'figure2_display',),
                       ('trial_type', 'trial_sub_type', 'trial_date'),
                       ('condition', 'description',),
                       ('figure1', 'figure2',),)
        }),
        ('Participants', {
            'fields': (
                ('species', 'gender', 'population_size',),
                ('age_min', 'age_max', 'age_average', 'age_unit',),
                ('weight_min', 'weight_max', 'weight_average', 'weight_unit'),
            )
        }),
        ('References', {
            'fields': (('source', 'references', 'source_link'),)
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
    inlines = [FindingResultInline]

    def source_page(self, obj):
        return '<a href="%s" target="_blank">%s</a>' % (obj.source_link, obj.source_link)
    source_page.allow_tags = True

admin.site.register(DrugTrial, DrugTrialAdmin)


class FindingTypeAdmin(LockableAdmin):
    list_per_page = 300
    save_on_top = True
    list_display = ('finding_type', 'description')
    fieldsets = (
        (
            None, {
                'fields': (
                    'finding_type',
                    'description',
                )
            }
        ),
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

admin.site.register(FindingType, FindingTypeAdmin)


class ResultDescriptorAdmin(LockableAdmin):
    list_per_page = 300
    save_on_top = True
    fieldsets = (
        (
            None, {
                'fields': (
                    'result_descriptor',
                )
            }
        ),
        (
            'Change Tracking', {
                'fields': (
                    'locked',
                    ('created_by', 'created_on'),
                    ('modified_by', 'modified_on'),
                    ('signed_off_by', 'signed_off_date'),
                )
            }
        ),
    )


admin.site.register(ResultDescriptor, ResultDescriptorAdmin)


class FindingAdmin(LockableAdmin):

    form = FindingForm

    save_on_top = True
    list_per_page = 300
    list_display = ('organ', 'finding_type', 'finding_name', 'optional_link')
    list_display_links = ('organ', 'finding_name', 'finding_type')
    list_filter = sorted(['finding_type'])
    search_fields = ['finding_name', ]
    fieldsets = (
        (
            None, {
                'fields': (
                    'finding_name',
                    'finding_type',
                    'organ',
                    'description',
                )
            }
        ),
        (
            'Change Tracking', {
                'fields': (
                    'locked',
                    ('created_by', 'created_on'),
                    ('modified_by', 'modified_on'),
                    ('signed_off_by', 'signed_off_date'),
                )
            }
        ),
    )
    actions = ['update_fields']

    def optional_link(self, obj):
        words = obj.description.split()
        sentence = ''
        for thing in words:
            if thing.startswith("http://"):
                link = '<a href="%s" target="_blank">%s</a>' % (thing, thing)
                sentence += (' ' + link)
            else:
                sentence += (' ' + thing)
        return sentence
    optional_link.allow_tags = True
    optional_link.short_description = "Description"


admin.site.register(Finding, FindingAdmin)


class AdverseEventAdmin(ImportExportModelAdmin):

    save_on_top = True
    list_per_page = 300
    list_display = ('event', 'organ')
    fieldsets = (
        (
            None, {
                'fields': (
                    'event',
                    'organ',
                )
            }
        ),
    )


admin.site.register(AdverseEvent, AdverseEventAdmin)
