"""Admin tools for assays alongside helper functions

Note that the code for templates can be found here
"""

# import csv

from django.contrib import admin
from django import forms
from django.contrib.auth.models import Group, User
# from assays.forms import (
#     AssayStudyConfigurationForm,
#     AssayChipReadoutInlineFormset,
#     AssayPlateReadoutInlineFormset,
# )
from assays.utils import (
    # save_assay_layout,
    # modify_qc_status_chip,
    # modify_qc_status_plate,
    DEFAULT_CSV_HEADER,
    # modify_templates
)
# TODO SPAGHETTI CODE
# from django.http import HttpResponseRedirect

from assays.models import (
    AssayQualityIndicator,
    UnitType,
    PhysicalUnits,
    AssayStudyModel,
    AssayStudyConfiguration,
    AssayTarget,
    AssaySampleLocation,
    AssayMeasurementType,
    AssaySupplier,
    AssayMethod,
    AssayStudyAssay,
    AssayStudySupportingData,
    AssayStudyStakeholder,
    AssayStudy,
    AssayMatrixItem,
    AssayMatrix,
    AssayImage,
    AssayImageSetting,
    AssaySetting,
    AssaySubtarget,
    AssayReference,
    AssayStudyReference,
    AssayStudySet,
    AssayCategory,
    SpeciesParameters,
    AssayPlateReaderMap,
    AssayPlateReaderMapItem,
    AssayPlateReaderMapDataFile,
    AssayPlateReaderMapDataFileBlock,
    AssayPlateReaderMapItemValue,
    # AssayOmicDataGroup,
    AssayOmicDataFileUpload,
    AssayOmicDataPoint,
    AssayOmicAnalysisTarget,
    AssayOmicSampleMetadata,
)
from microdevices.models import MicrophysiologyCenter
# from compounds.models import Compound
from mps.base.admin import LockableAdmin
# from assays.resource import *
# from import_export.admin import ImportExportModelAdmin
# from compounds.models import *
# import unicodedata
# from io import BytesIO
# import ujson as json
# I use regular expressions for a string split at one point
# import re
# from django.db import connection, transaction
# from urllib import unquote

from .forms import AssayStudyFormAdmin #, AssayStudyConfigurationForm

# import os
# import xlsxwriter
# from xlsxwriter.utility import xl_col_to_name

from django.template.loader import render_to_string, TemplateDoesNotExist
from mps.settings import DEFAULT_FROM_EMAIL
from mps.templatetags.custom_filters import (
    ADMIN_SUFFIX,
    VIEWER_SUFFIX,
)

from datetime import datetime, timedelta
import pytz

from import_export.admin import ImportExportModelAdmin

from django.utils.safestring import mark_safe


# DEPRECATED
class AssayQualityIndicatorFormAdmin(forms.ModelForm):
    """Admin Form for Quality Indicators"""
    class Meta(object):
        model = AssayQualityIndicator
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10}),
        }
        exclude = ('',)


class UnitTypeFormAdmin(forms.ModelForm):
    """Admin Form for Unit Types"""
    class Meta(object):
        model = UnitType
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10}),
        }
        exclude = ('',)


class UnitTypeAdmin(LockableAdmin):
    """Admin for Unit Types"""
    form = UnitTypeFormAdmin

    save_on_top = True
    list_per_page = 300
    list_display = ('unit_type', 'description')
    search_fields = ('unit_type', 'description')
    fieldsets = (
        (
            None, {
                'fields': (
                    ('unit_type', 'description'),
                )
            }
        ),
        ('Change Tracking', {
            'fields': (
                # 'locked',
                ('created_by', 'created_on'),
                ('modified_by', 'modified_on'),
                ('signed_off_by', 'signed_off_date'),
            )
        }
        ),
    )


admin.site.register(UnitType, UnitTypeAdmin)


class PhysicalUnitsFormAdmin(forms.ModelForm):
    """Admin Form for Physical Units"""
    class Meta(object):
        model = PhysicalUnits
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10}),
        }
        exclude = ('',)


class PhysicalUnitsAdmin(LockableAdmin):
    """Admin for Units

    Note that all assay units should link to Physical Units
    """
    form = PhysicalUnitsFormAdmin

    save_on_top = True
    list_per_page = 300
    list_display = ('unit_type', 'unit', 'base_unit', 'scale_factor', 'availability', 'description')
    search_fields = ('unit_type__unit_type', 'unit', 'availability', 'description')
    fieldsets = (
        (
            None, {
                'fields': (
                    'unit',
                    'unit_type',
                    ('base_unit', 'scale_factor'),
                    'availability',
                    'description',
                )
            }
        ),
        ('Change Tracking', {
            'fields': (
                # 'locked',
                ('created_by', 'created_on'),
                ('modified_by', 'modified_on'),
                ('signed_off_by', 'signed_off_date'),
            )
        }
        ),
    )

    def save_model(self, request, obj, form, change):
        # Strip the name
        form.instance.unit = form.instance.unit.strip()
        obj.unit = obj.unit.strip()

        if change:
            obj.modified_by = request.user
        else:
            obj.modified_by = obj.created_by = request.user

        obj.save()


admin.site.register(PhysicalUnits, PhysicalUnitsAdmin)


class AssayStudyModelInline(admin.TabularInline):
    """Inline for Study Configurations"""
    model = AssayStudyModel
    verbose_name = 'Study Model'
    fields = (
        (
            'label', 'organ', 'sequence_number', 'output', 'integration_mode',
        ),
    )
    extra = 1

    class Media(object):
        css = {'all': ('css/hide_admin_original.css',)}


class AssayStudyConfigurationAdmin(LockableAdmin):
    """Admin for study configurations"""

    class Media(object):
        js = ('js/inline_fix.js',)

    # form = AssayStudyConfigurationForm
    save_on_top = True
    list_per_page = 300
    list_display = ('name',)
    fieldsets = (
        (
            'Study Configuration', {
                'fields': (
                    'name',
                    'media_composition',
                    'hardware_description',
                )
            }
        ),
        (
            'Change Tracking', {
                'fields': (
                    # 'locked',
                    ('created_by', 'created_on'),
                    ('modified_by', 'modified_on'),
                    ('signed_off_by', 'signed_off_date'),
                )
            }
        ),
    )
    inlines = [AssayStudyModelInline]


admin.site.register(AssayStudyConfiguration, AssayStudyConfigurationAdmin)


class AssayTargetFormAdmin(forms.ModelForm):
    """Admin Form for Targets"""
    class Meta(object):
        model = AssayTarget
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10}),
            'name': forms.Textarea(attrs={'rows': 2}),
            'alt_name': forms.Textarea(attrs={'rows': 2}),
        }
        exclude = ('',)


# TODO MAKE A VARIABLE TO CONTAIN TRACKING DATA TO AVOID COPY/PASTE
class AssayTargetAdmin(LockableAdmin):
    # model = AssayTarget
    form = AssayTargetFormAdmin

    save_on_top = True
    list_per_page = 300
    list_display = (
        'name',
        'short_name',
        'alt_name',
        'description'
    )
    search_fields = (
        'name',
        'short_name',
        'description'
    )
    filter_horizontal = ('methods',)
    fieldsets = (
        (
            'Target', {
                'fields': (
                    'name',
                    'alt_name',
                    'short_name',
                    'description',
                    'methods'
                )
            }
        ),
        (
            'Change Tracking', {
                'fields': (
                    # 'locked',
                    ('created_by', 'created_on'),
                    ('modified_by', 'modified_on'),
                    ('signed_off_by', 'signed_off_date'),
                )
            }
        ),
    )

    def save_model(self, request, obj, form, change):
        # Strip the name and short name
        form.instance.name = form.instance.name.strip()
        form.instance.short_name = form.instance.short_name.strip()
        obj.name = obj.name.strip()
        obj.short_name = obj.short_name.strip()

        if change:
            obj.modified_by = request.user
        else:
            obj.modified_by = obj.created_by = request.user

        obj.save()


admin.site.register(AssayTarget, AssayTargetAdmin)


class AssaySampleLocationFormAdmin(forms.ModelForm):
    """Admin Form for Sample Locations"""
    class Meta(object):
        model = AssaySampleLocation
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10}),
        }
        exclude = ('',)


class AssaySampleLocationAdmin(LockableAdmin):
    # model = AssaySampleLocation

    form = AssaySampleLocationFormAdmin

    save_on_top = True
    list_per_page = 300
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    fieldsets = (
        (
            'Sample Location', {
                'fields': (
                    'name',
                    'description',
                )
            }
        ),
        (
            'Change Tracking', {
                'fields': (
                    # 'locked',
                    ('created_by', 'created_on'),
                    ('modified_by', 'modified_on'),
                    ('signed_off_by', 'signed_off_date'),
                )
            }
        ),
    )

    def save_model(self, request, obj, form, change):
        # Strip the name
        form.instance.name = form.instance.name.strip()
        obj.name = obj.name.strip()

        if change:
            obj.modified_by = request.user
        else:
            obj.modified_by = obj.created_by = request.user

        obj.save()

admin.site.register(AssaySampleLocation, AssaySampleLocationAdmin)


class AssayMeasurementTypeFormAdmin(forms.ModelForm):
    """Admin Form for Measurement Types"""
    class Meta(object):
        model = AssayMeasurementType
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10}),
        }
        exclude = ('',)


class AssayMeasurementTypeAdmin(LockableAdmin):
    # model = AssayMeasurementType

    form = AssayMeasurementTypeFormAdmin

    save_on_top = True
    list_per_page = 300
    list_display = ('name', 'description')
    search_fields = (
        'name',
        'description'
    )
    fieldsets = (
        (
            'Measurement Type', {
                'fields': (
                    'name',
                    'description',
                )
            }
        ),
        (
            'Change Tracking', {
                'fields': (
                    # 'locked',
                    ('created_by', 'created_on'),
                    ('modified_by', 'modified_on'),
                    ('signed_off_by', 'signed_off_date'),
                )
            }
        ),
    )

admin.site.register(AssayMeasurementType, AssayMeasurementTypeAdmin)


class AssaySupplierFormAdmin(forms.ModelForm):
    """Admin Form for Suppliers"""
    class Meta(object):
        model = AssaySupplier
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10}),
        }
        exclude = ('',)


class AssaySupplierAdmin(LockableAdmin):
    # model = AssaySupplier

    form = AssaySupplierFormAdmin

    save_on_top = True
    list_per_page = 300
    list_display = ('name', 'description')
    search_fields = (
        'name',
        'description'
    )
    fieldsets = (
        (
            'Measurement Type', {
                'fields': (
                    'name',
                    'description',
                )
            }
        ),
        (
            'Change Tracking', {
                'fields': (
                    # 'locked',
                    ('created_by', 'created_on'),
                    ('modified_by', 'modified_on'),
                    ('signed_off_by', 'signed_off_date'),
                )
            }
        ),
    )

admin.site.register(AssaySupplier, AssaySupplierAdmin)


class AssayMethodFormAdmin(forms.ModelForm):
    """Admin Form for Methods"""
    class Meta(object):
        model = AssayMethod
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10}),
            'name': forms.Textarea(attrs={'rows': 2}),
            'alt_name': forms.Textarea(attrs={'rows': 2}),
        }
        exclude = ('',)


class AssayMethodAdmin(LockableAdmin):
    # model = AssayMethod

    form = AssayMethodFormAdmin

    save_on_top = True
    list_per_page = 300
    list_display = (
        'name',
        'alt_name',
        'measurement_type',
        'supplier',
        'protocol_file',
        'description'
    )
    search_fields = (
        'name',
        'description'
    )
    fieldsets = (
        (
            'Measurement Type', {
                'fields': (
                    'name',
                    'alt_name',
                    'description',
                    'measurement_type',
                    'supplier',
                    'protocol_file'
                )
            }
        ),
        (
            'Change Tracking', {
                'fields': (
                    # 'locked',
                    ('created_by', 'created_on'),
                    ('modified_by', 'modified_on'),
                    ('signed_off_by', 'signed_off_date'),
                )
            }
        ),
    )

    def save_model(self, request, obj, form, change):
        # Strip the name
        form.instance.name = form.instance.name.strip()
        obj.name = obj.name.strip()

        if change:
            obj.modified_by = request.user
        else:
            obj.modified_by = obj.created_by = request.user

        obj.save()

admin.site.register(AssayMethod, AssayMethodAdmin)

# admin.site.register(AssayStudyType)


class AssayStudyAssayInline(admin.TabularInline):
    model = AssayStudyAssay
    exclude = []

    # TODO REVIEW
    # TODO NOT DRY
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'target':
            target_queryset = AssayTarget.objects.all().order_by('name')
            kwargs["queryset"] = target_queryset
        elif db_field.name == 'method':
            method_queryset = AssayMethod.objects.all().order_by('name')
            kwargs["queryset"] = method_queryset
        elif db_field.name == 'unit':
            unit_queryset = PhysicalUnits.objects.all().order_by('unit_type__unit_type', 'base_unit__unit', 'scale_factor')
            kwargs["queryset"] = unit_queryset
        return super(AssayStudyAssayInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class AssayStudySupportingDataInline(admin.TabularInline):
    """Inline for Studies"""
    model = AssayStudySupportingData
    verbose_name = 'Study Supporting Data'
    fields = (
        (
            'description', 'supporting_data'
        ),
    )
    extra = 1

# class AssayOmicDataGroupInline(admin.TabularInline):
#     """Inline for Studies"""
#     model = AssayOmicDataGroup
#     verbose_name = 'Assay Omic Data Group - Temporary Group Options'
#     fields = (
#         (
#             'name', 'number'
#         ),
#     )
#     extra = 1


# TODO REMAKE FOR ASSAY STUDY
class AssayStudyStakeholderInline(admin.TabularInline):
    """Inline for Studies"""
    model = AssayStudyStakeholder
    verbose_name = 'Study Stakeholders (Level 1)'
    extra = 1

    # TODO REVIEW
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "group":
            groups_with_center = MicrophysiologyCenter.objects.all().values_list('groups', flat=True)
            groups_with_center_full = Group.objects.filter(
                id__in=groups_with_center
            ).order_by(
                'name'
            )
            kwargs["queryset"] = groups_with_center_full
        return super(AssayStudyStakeholderInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class AssayStudyReferenceInline(admin.TabularInline):
    """Inline for Studies"""
    model = AssayStudyReference
    exclude = []
    extra = 1


# TODO REMAKE FOR ASSAY STUDY
class AssayStudyAdmin(LockableAdmin):
    """Admin for Studies"""
    # class Media(object):
    #     js = ('assays/assaystudy_add.js',)

    form = AssayStudyFormAdmin
    save_on_top = True
    list_per_page = 300
    search_fields = ('name', 'group__name', 'start_date', 'description')
    date_hierarchy = 'start_date'
    list_display = (
        'name',
        'id',
        'group',
        'get_study_types_string',
        'start_date',
        'signed_off_by',
        'signed_off_date',
        'stakeholder_display',
        'access_group_display',
        'collaborator_group_display',
        'restricted',
        'locked',
        # 'description',
    )

    filter_horizontal = ('access_groups', 'collaborator_groups')

    fieldsets = (
        (
            'Study', {
                'fields': (
                    ('toxicity', 'efficacy', 'disease', 'cell_characterization', 'omics'),
                    'study_configuration',
                    'start_date',
                    'name',
                    'description',
                    'use_in_calculations',
                    'image',
                )
            }
        ),
        (
            'PBPK', {
                'fields': (
                    'pbpk_steady_state',
                    'pbpk_bolus',
                    'number_of_relevant_cells',
                    'total_device_volume',
                    'flow_rate',
                )
            }
        ),
        (
            'Protocol File Upload', {
                'fields': (
                    'protocol',
                )
            }
        ),
        (
            'Change Tracking', {
                'fields': (
                    # 'locked',
                    ('created_by', 'created_on'),
                    ('modified_by', 'modified_on'),
                    ('signed_off_by', 'signed_off_date'),
                    ('signed_off_notes',),
                    ('flagged', 'reason_for_flag')
                )
            }
        ),
        (
            'Study Data Group and Access Group Info', {
                'fields': (
                    'group', 'restricted', 'locked', 'access_groups', 'collaborator_groups'
                ),
            },
        ),
    )

    # inlines = [AssayStudyStakeholderInline, AssayStudyAssayInline, AssayStudySupportingDataInline, AssayStudyReferenceInline, AssayOmicDataGroupInline]
    inlines = [AssayStudyStakeholderInline, AssayStudyAssayInline, AssayStudySupportingDataInline, AssayStudyReferenceInline]

    def get_queryset(self, request):
        qs = super(AssayStudyAdmin, self).get_queryset(request)
        qs = qs.prefetch_related(
            'access_groups',
            'collaborator_groups',
            # Needs to be revised to actually improve time
            'assaystudystakeholder_set__group',
            # 'assaystudystakeholder_set__signed_off_by',
            'signed_off_by',
        )
        return qs

    # Not a, uh, great query. Way too large.
    @mark_safe
    def stakeholder_display(self, obj):
        contents = ''
        trigger = ''
        queryset = obj.assaystudystakeholder_set.all()
        count = queryset.count()
        released = True

        if count:
            stakes = []
            for stakeholder in queryset.order_by('group__name'):
                if not stakeholder.signed_off_by_id:
                    released = False
                    current_approval_status = False
                else:
                    current_approval_status = True

                stakes.append('{0} Approved?: {1}'.format(stakeholder.group.name, current_approval_status))

            contents = '<br>'.join(stakes)

            if released:
                released = 'Approved!'
            else:
                released = ''

            trigger = '<a href="javascript:void(0)" onclick=$("#stakes_{0}").toggle()>Show/Hide Stakeholders ({1}) {2}</a>'.format(
                obj.pk, count, released
            )
        return '{0}<div hidden id="stakes_{1}">{2}</div>'.format(trigger, obj.pk, contents)

    stakeholder_display.allow_tags = True

    @mark_safe
    def access_group_display(self, obj):
        contents = ''
        trigger = ''
        queryset = obj.access_groups.all()
        count = queryset.count()

        if count:
            contents = '<br>'.join(
                [
                    group.name for group in queryset.order_by('name')
                ]
            )
            trigger = '<a href="javascript:void(0)" onclick=$("#access_{0}").toggle()>Show/Hide Access Groups ({1})</a>'.format(
                obj.pk, count
            )
        return '{0}<div hidden id="access_{1}">{2}</div>'.format(trigger, obj.pk, contents)

    access_group_display.allow_tags = True

    @mark_safe
    def collaborator_group_display(self, obj):
        contents = ''
        trigger = ''
        queryset = obj.collaborator_groups.all()
        count = queryset.count()

        if count:
            contents = '<br>'.join(
                [
                    group.name for group in queryset.order_by('name')
                ]
            )
            trigger = '<a href="javascript:void(0)" onclick=$("#collaborator_{0}").toggle()>Show/Hide Collaborator Groups ({1})</a>'.format(
                obj.pk, count
            )
        return '{0}<div hidden id="collaborator_{1}">{2}</div>'.format(trigger, obj.pk, contents)

    collaborator_group_display.allow_tags = True

    # save_related takes the place of save_model so that the inline can be referred to
    # TODO TODO TODO THIS IS NOT VERY DRY
    # This code may pose a problem if multiple people are editing an entry at once...
    def save_related(self, request, form, formsets, change):
        # Local datetime
        tz = pytz.timezone('US/Eastern')
        datetime_now_local = datetime.now(tz)
        fourteen_days_from_date = datetime_now_local + timedelta(days=14)

        send_initial_sign_off_alert = False

        # SAVE FORM HERE
        # TODO TODO TODO

        if change:
            initial_study = AssayStudy.objects.get(pk=form.instance.id)
            initial_sign_off = initial_study.signed_off_by
            initial_restricted = initial_study.restricted
            initial_required_stakeholders = AssayStudyStakeholder.objects.filter(
                study_id=initial_study.id,
                signed_off_by_id=None,
                sign_off_required=True
            )
            initial_required_stakeholder_group_ids = list(initial_required_stakeholders.values_list('group_id', flat=True))
            previous_access_groups = {group.name: group.id for group in initial_study.access_groups.all()}

            obj = form.save()
            obj.modified_by = request.user
            obj.save()

            if not initial_sign_off and obj.signed_off_by:
                send_initial_sign_off_alert = True

        else:
            initial_study = form.instance
            initial_sign_off = initial_study.signed_off_by
            initial_restricted = initial_study.restricted
            initial_required_stakeholders = AssayStudyStakeholder.objects.none()
            initial_required_stakeholder_group_ids = list(initial_required_stakeholders.values_list('group_id', flat=True))
            previous_access_groups = {}

            obj = form.save()
            obj.modified_by = obj.created_by = request.user
            obj.save()

        if change:
            initial_number_of_required_sign_offs = initial_required_stakeholders.count()
        else:
            initial_number_of_required_sign_offs = 0

        viewer_subject = 'Study {0} Now Available for Viewing'.format(initial_study)

        # SAVE FORMSETS HERE
        # TODO TODO TODO
        # Save inline and many to many
        super(AssayStudyAdmin, self).save_related(request, form, formsets, change)

        # Crude way to make sure M2M is up-to-date
        study_after_save = AssayStudy.objects.get(pk=form.instance.id)

        new_access_group_names = {
            group.name: group.id for group in study_after_save.access_groups.all() if
            group.name not in previous_access_groups
        }

        current_number_of_required_sign_offs = AssayStudyStakeholder.objects.filter(
            study_id=obj.id,
            signed_off_by_id=None,
            sign_off_required=True
        ).count()

        send_stakeholder_sign_off_alert = current_number_of_required_sign_offs < initial_number_of_required_sign_offs

        # TODO TODO TODO
        # ONLY SEND VIEWER ALERT IF:
        # Sign off occurred and no stakeholders
        # Sign off occurred and final stakeholder has acknowledged
        # send_viewer_alert = current_number_of_required_sign_offs == 0 and obj.signed_off_by
        send_viewer_alert = (
            send_initial_sign_off_alert and current_number_of_required_sign_offs == 0
        ) or (
            obj.signed_off_by and current_number_of_required_sign_offs == 0 and send_stakeholder_sign_off_alert
        )

        # TODO TODO TODO TODO
        # stakeholder_admin_subject = 'Acknowledgement of Study {0} Requested'.format(obj)
        stakeholder_admin_subject = 'Approval for Release Requested: {0}'.format(obj)

        stakeholder_viewer_groups = {}
        stakeholder_admin_groups = {}

        stakeholder_admins_to_be_alerted = []
        stakeholder_viewers_to_be_alerted = []

        # VULGAR! NOT DRY
        # PASTED HERE
        if send_initial_sign_off_alert:
            # TODO TODO TODO TODO ALERT STAKEHOLDER ADMINS
            stakeholder_admin_groups = {
                group + ADMIN_SUFFIX: True for group in
                AssayStudyStakeholder.objects.filter(
                    study_id=obj.id, sign_off_required=True
                ).prefetch_related('group').values_list('group__name', flat=True)
            }

            stakeholder_admins_to_be_alerted = User.objects.filter(
                groups__name__in=stakeholder_admin_groups, is_active=True
            ).distinct()

            for user_to_be_alerted in stakeholder_admins_to_be_alerted:
                try:
                    stakeholder_admin_message = render_to_string(
                        'assays/email/tctc_stakeholder_email.txt',
                        {
                            'user': user_to_be_alerted,
                            'study': obj,
                            'fourteen_days_from_date': fourteen_days_from_date
                        }
                    )
                except TemplateDoesNotExist:
                    stakeholder_admin_message = render_to_string(
                        'assays/email/stakeholder_sign_off_request.txt',
                        {
                            'user': user_to_be_alerted,
                            'study': obj
                        }
                    )

                user_to_be_alerted.email_user(
                    stakeholder_admin_subject,
                    stakeholder_admin_message,
                    DEFAULT_FROM_EMAIL
                )

            # TODO TODO TODO TODO ALERT STAKEHOLDER VIEWERS
            stakeholder_viewer_groups = {
                group: True for group in
                AssayStudyStakeholder.objects.filter(
                    study_id=obj.id
                ).prefetch_related('group').values_list('group__name', flat=True)
            }
            initial_groups = list(stakeholder_viewer_groups.keys())

            for group in initial_groups:
                stakeholder_viewer_groups.update({
                    # group + ADMIN_SUFFIX: True,
                    group + VIEWER_SUFFIX: True
                })

            # BE SURE THIS IS MATCHED BELOW
            stakeholder_viewers_to_be_alerted = User.objects.filter(
                groups__name__in=stakeholder_viewer_groups, is_active=True
            ).exclude(
                id__in=stakeholder_admins_to_be_alerted
            ).distinct()

            for user_to_be_alerted in stakeholder_viewers_to_be_alerted:
                # TODO TODO TODO WHAT DO WE CALL THE PROCESS OF SIGN OFF ACKNOWLEDGEMENT?!
                viewer_message = render_to_string(
                    'assays/email/viewer_alert.txt',
                    {
                        'user': user_to_be_alerted,
                        'study': obj
                    }
                )

                user_to_be_alerted.email_user(
                    viewer_subject,
                    viewer_message,
                    DEFAULT_FROM_EMAIL
                )

        if send_viewer_alert:
            access_group_names = {group.name: group.id for group in obj.access_groups.all()}
            matching_groups = list(set([
                group.id for group in Group.objects.all() if
                group.name.replace(ADMIN_SUFFIX, '').replace(VIEWER_SUFFIX, '') in access_group_names
            ]))
            # Just in case, exclude stakeholders to prevent double messages
            viewers_to_be_alerted = User.objects.filter(
                groups__id__in=matching_groups, is_active=True
            ).exclude(
                id__in=stakeholder_admins_to_be_alerted
            ).exclude(
                id__in=stakeholder_viewers_to_be_alerted
            ).distinct()
            # Update viewer groups to include admins
            stakeholder_viewer_groups.update(stakeholder_admin_groups)
            # if stakeholder_viewer_groups or stakeholder_admin_groups:
            #     viewers_to_be_alerted.exclude(
            #         groups__name__in=stakeholder_viewer_groups
            #     ).exclude(
            #         group__name__in=stakeholder_admin_groups
            #     )

            for user_to_be_alerted in viewers_to_be_alerted:
                viewer_message = render_to_string(
                    'assays/email/viewer_alert.txt',
                    {
                        'user': user_to_be_alerted,
                        'study': obj
                    }
                )

                user_to_be_alerted.email_user(
                    viewer_subject,
                    viewer_message,
                    DEFAULT_FROM_EMAIL
                )

        # Superusers to contact
        superusers_to_be_alerted = User.objects.filter(is_superuser=True, is_active=True)

        if send_initial_sign_off_alert:
            # Magic strings are in poor taste, should use a template instead
            superuser_subject = 'Study Sign Off Detected: {0}'.format(obj)
            superuser_message = render_to_string(
                'assays/email/superuser_initial_sign_off_alert.txt',
                {
                    'study': obj,
                    'stakeholders': AssayStudyStakeholder.objects.filter(study_id=obj.id).order_by('-signed_off_date')
                }
            )

            for user_to_be_alerted in superusers_to_be_alerted:
                user_to_be_alerted.email_user(superuser_subject, superuser_message, DEFAULT_FROM_EMAIL)

        if send_stakeholder_sign_off_alert:
            # Magic strings are in poor taste, should use a template instead
            # superuser_subject = 'Stakeholder Acknowledgement Detected: {0}'.format(obj)
            superuser_subject = 'Stakeholder Approval Detected: {0}'.format(obj)
            superuser_message = render_to_string(
                'assays/email/superuser_stakeholder_alert.txt',
                {
                    'study': obj,
                    'stakeholders': AssayStudyStakeholder.objects.filter(study_id=obj.id).order_by('-signed_off_date')
                }
            )

            for user_to_be_alerted in superusers_to_be_alerted:
                user_to_be_alerted.email_user(superuser_subject, superuser_message, DEFAULT_FROM_EMAIL)

        if send_viewer_alert:
            # Magic strings are in poor taste, should use a template instead
            superuser_subject = 'Study Released to Next Level: {0}'.format(obj)
            superuser_message = render_to_string(
                'assays/email/superuser_viewer_release_alert.txt',
                {
                    'study': obj
                }
            )

            for user_to_be_alerted in superusers_to_be_alerted:
                user_to_be_alerted.email_user(superuser_subject, superuser_message, DEFAULT_FROM_EMAIL)
        # END PASTE

        # Special alerts for adding a stakeholder after sign off
        # Will send a message to all required admins and viewers
        # BE SURE NOT TO SEND TO STAKEHOLDERS THAT HAVE ALREADY SIGNED OFF
        if obj.signed_off_by and not send_initial_sign_off_alert and initial_number_of_required_sign_offs < current_number_of_required_sign_offs:
            # ...
            # UGLY NOT DRY
            stakeholder_admin_groups = {
                group + ADMIN_SUFFIX: True for group in
                AssayStudyStakeholder.objects.filter(
                    study_id=obj.id, sign_off_required=True, signed_off_by_id=None
                ).exclude(
                    # id__in=initial_required_stakeholders
                    group_id__in=initial_required_stakeholder_group_ids
                ).prefetch_related('group').values_list('group__name', flat=True)
            }

            stakeholder_admins_to_be_alerted = User.objects.filter(
                groups__name__in=stakeholder_admin_groups, is_active=True
            ).distinct()

            for user_to_be_alerted in stakeholder_admins_to_be_alerted:
                try:
                    stakeholder_admin_message = render_to_string(
                        'assays/email/tctc_stakeholder_email.txt',
                        {
                            'user': user_to_be_alerted,
                            'study': obj,
                            'fourteen_days_from_date': fourteen_days_from_date
                        }
                    )
                except TemplateDoesNotExist:
                    stakeholder_admin_message = render_to_string(
                        'assays/email/stakeholder_sign_off_request.txt',
                        {
                            'user': user_to_be_alerted,
                            'study': obj
                        }
                    )

                user_to_be_alerted.email_user(
                    stakeholder_admin_subject,
                    stakeholder_admin_message,
                    DEFAULT_FROM_EMAIL
                )

            # TODO TODO TODO TODO ALERT STAKEHOLDER VIEWERS
            stakeholder_viewer_groups = {
                group: True for group in
                AssayStudyStakeholder.objects.filter(
                    study_id=obj.id, signed_off_by_id=None
                ).exclude(
                    # id__in=initial_required_stakeholders
                    group_id__in=initial_required_stakeholder_group_ids
                ).prefetch_related('group').values_list('group__name', flat=True)
            }
            initial_groups = list(stakeholder_viewer_groups.keys())

            for group in initial_groups:
                stakeholder_viewer_groups.update({
                    # group + ADMIN_SUFFIX: True,
                    group + VIEWER_SUFFIX: True
                })

            stakeholder_viewers_to_be_alerted = User.objects.filter(
                groups__name__in=stakeholder_viewer_groups, is_active=True
            ).exclude(
                id__in=stakeholder_admins_to_be_alerted
            ).distinct()

            for user_to_be_alerted in stakeholder_viewers_to_be_alerted:
                # TODO TODO TODO WHAT DO WE CALL THE PROCESS OF SIGN OFF ACKNOWLEDGEMENT?!
                viewer_message = render_to_string(
                    'assays/email/viewer_alert.txt',
                    {
                        'user': user_to_be_alerted,
                        'study': obj
                    }
                )

                user_to_be_alerted.email_user(
                    viewer_subject,
                    viewer_message,
                    DEFAULT_FROM_EMAIL
                )

        # Special alerts for new access groups
        if not send_viewer_alert and new_access_group_names and obj.signed_off_by and current_number_of_required_sign_offs == 0:
            matching_groups = list(set([
                group.id for group in Group.objects.all() if
                group.name.replace(ADMIN_SUFFIX, '').replace(VIEWER_SUFFIX, '') in new_access_group_names
            ]))
            exclude_groups = list(set([
                group.id for group in Group.objects.all() if
                group.name.replace(ADMIN_SUFFIX, '').replace(VIEWER_SUFFIX, '') in previous_access_groups
            ]))
            viewers_to_be_alerted = User.objects.filter(
                groups__id__in=matching_groups,
                is_active=True
            ).exclude(
                groups__id__in=exclude_groups
            ).distinct()

            for user_to_be_alerted in viewers_to_be_alerted:
                viewer_message = render_to_string(
                    'assays/email/viewer_alert.txt',
                    {
                        'user': user_to_be_alerted,
                        'study': obj
                    }
                )

                user_to_be_alerted.email_user(
                    viewer_subject,
                    viewer_message,
                    DEFAULT_FROM_EMAIL
                )

            # TODO CHANGE SUPERUSER VIEWER RELEASE ALERT
            # Magic strings are in poor taste, should use a template instead
            superuser_subject = 'Study Released to Next Level: {0}'.format(obj)
            superuser_message = render_to_string(
                'assays/email/superuser_viewer_release_alert.txt',
                {
                    'study': obj,
                    'new_access_group_names': new_access_group_names
                }
            )

            for user_to_be_alerted in superusers_to_be_alerted:
                user_to_be_alerted.email_user(superuser_subject, superuser_message, DEFAULT_FROM_EMAIL)

        # Special case for going public
        if initial_restricted and not obj.restricted:
            # Magic strings are in poor taste, should use a template instead
            superuser_subject = 'Study Released to Next Level: {0}'.format(obj)
            superuser_message = render_to_string(
                'assays/email/superuser_viewer_release_alert.txt',
                {
                    'study': obj,
                    'new_access_group_names': []
                }
            )

            for user_to_be_alerted in superusers_to_be_alerted:
                user_to_be_alerted.email_user(superuser_subject, superuser_message, DEFAULT_FROM_EMAIL)

    # Odd, I know, but prevents double save
    def save_model(self, request, obj, form, change):
        pass


admin.site.register(AssayStudy, AssayStudyAdmin)


# TODO TODO TODO TODO NEW MODELS HERE
class AssayMatrixItemAdmin(ImportExportModelAdmin):
    model = AssayMatrixItem
    search_fields = ('name', 'notes')

admin.site.register(AssayMatrixItem, AssayMatrixItemAdmin)


class AssayMatrixAdmin(ImportExportModelAdmin):
    model = AssayMatrix
    search_fields = ('name', 'notes')

admin.site.register(AssayMatrix, AssayMatrixAdmin)


class AssayImageAdmin(ImportExportModelAdmin):
    model = AssayImage
    search_fields = ('matrix_item__name', 'file_name')

admin.site.register(AssayImage, AssayImageAdmin)


class AssayImageSettingAdmin(ImportExportModelAdmin):
    model = AssayImageSetting
    search_fields = ('study__name', 'label_name')

admin.site.register(AssayImageSetting, AssayImageSettingAdmin)


class AssaySettingAdmin(ImportExportModelAdmin):
    model = AssaySetting
    search_fields = ('name', 'description')

admin.site.register(AssaySetting, AssaySettingAdmin)


class AssaySubtargetAdmin(ImportExportModelAdmin):
    model = AssaySubtarget
    search_fields = ('name', 'description')

admin.site.register(AssaySubtarget, AssaySubtargetAdmin)


class AssayReferenceAdmin(ImportExportModelAdmin):
    model = AssayReference
    search_fields = ('pubmed_id', 'title', 'authors')

admin.site.register(AssayReference, AssayReferenceAdmin)


class AssayStudySetAdminForm(forms.ModelForm):
    class Meta(object):
        model = AssayStudySet
        exclude = ('',)
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10})
        }

    def __init__(self, *args, **kwargs):
        super(AssayStudySetAdminForm, self).__init__(*args, **kwargs)
        study_queryset = AssayStudy.objects.all().prefetch_related(
            'group__center_groups'
        )
        assay_queryset = AssayStudyAssay.objects.all().prefetch_related(
            'target',
            'method',
            'unit',
        )

        self.fields['studies'].queryset = study_queryset
        self.fields['assays'].queryset = assay_queryset


class AssayStudySetAdmin(ImportExportModelAdmin):
    model = AssayStudySet
    form = AssayStudySetAdminForm
    search_fields = ('name', 'description')

admin.site.register(AssayStudySet, AssayStudySetAdmin)


class AssayCategoryAdmin(ImportExportModelAdmin):
    model = AssayCategory
    search_fields = ('name', 'description')
    filter_horizontal = ('targets',)

admin.site.register(AssayCategory, AssayCategoryAdmin)


class SpeciesParametersAdmin(ImportExportModelAdmin):
    model = SpeciesParameters
    search_fields = ('species', 'organ', 'reference')

admin.site.register(SpeciesParameters, SpeciesParametersAdmin)


# do not want to allow editing of the wells in the plate in the admin
# the relationship between the item and item value tables needs to be controlled by the GUI
class AssayPlateReaderMapAdmin(ImportExportModelAdmin):
    model = AssayPlateReaderMap
    list_display = ('name', 'description', 'device', 'study_assay', 'time_unit', 'volume_unit', 'cell_count')
    search_fields = ('name', 'description')

admin.site.register(AssayPlateReaderMap, AssayPlateReaderMapAdmin)

class AssayPlateReaderMapDataFileAdmin(ImportExportModelAdmin):
    model = AssayPlateReaderMapDataFile
    list_display = ('description', )
    search_fields = ('description',)

admin.site.register(AssayPlateReaderMapDataFile, AssayPlateReaderMapDataFileAdmin)

class AssayPlateReaderMapDataFileBlockAdmin(ImportExportModelAdmin):
    model = AssayPlateReaderMapDataFileBlock
    list_display = ('assayplatereadermap', 'assayplatereadermapdatafile', 'data_block', 'data_processing_parsable')
    search_fields = ('data_block',)

admin.site.register(AssayPlateReaderMapDataFileBlock, AssayPlateReaderMapDataFileBlockAdmin)

# class AssayOmicDataGroupAdmin(ImportExportModelAdmin):
#     model = AssayOmicDataGroup
#     list_display = ('name', 'number', 'study')
#     search_fields = ('name', 'study')
#
# admin.site.register(AssayOmicDataGroup, AssayOmicDataGroupAdmin)

class AssayOmicDataFileUploadAdmin(ImportExportModelAdmin):
    model = AssayOmicDataFileUpload
    list_display = ('description', 'study', 'omic_data_file', 'study_assay', 'analysis_method', 'data_type',
                    'group_1', 'group_2', 'time_1', 'time_2', 'location_1', 'location_2', 'name_reference')
    search_fields = ('description', )

admin.site.register(AssayOmicDataFileUpload, AssayOmicDataFileUploadAdmin)

class AssayOmicDataPointAdmin(ImportExportModelAdmin):
    model = AssayOmicDataPoint
    list_display = ('study', 'omic_data_file', 'name', 'analysis_target', 'value')
    search_fields = ('name', 'analysis_target', 'study', 'omic_data_file')

admin.site.register(AssayOmicDataPoint, AssayOmicDataPointAdmin)

class AssayOmicAnalysisTargetAdmin(ImportExportModelAdmin):
    """Admin for Analysis Targets"""
    model = AssayOmicAnalysisTarget
    list_display = ('name', 'target', 'data_type', 'method', 'unit')
    search_fields = ('name', 'target', 'data_type', 'method', 'unit')

    list_editable = ('target', 'data_type', 'method', 'unit')

admin.site.register(AssayOmicAnalysisTarget, AssayOmicAnalysisTargetAdmin)

class AssayOmicSampleMetadataAdmin(ImportExportModelAdmin):
    """Admin for Sample Metadata"""
    model = AssayOmicSampleMetadata
    list_display = ('study', 'sample_name', 'matrix_item', 'sample_location', 'sample_time')
    search_fields = ('study', 'sample_name', 'matrix_item', 'sample_location', 'sample_time')

admin.site.register(AssayOmicSampleMetadata, AssayOmicSampleMetadataAdmin)
