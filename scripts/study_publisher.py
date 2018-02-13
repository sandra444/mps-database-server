"""
    This script finds studies that either have been released to Level 2
    (either because they have no stakeholders or every stakeholder approved)
    and moves them to the public automatically after approximately one year's time
"""
from assays.models import AssayRun, AssayRunStakeholder
from datetime import datetime, timedelta
import pytz

from django.contrib.auth.models import User

from django.template.loader import render_to_string, TemplateDoesNotExist
from mps.settings import DEFAULT_FROM_EMAIL


def run():
    """Main function that runs the script"""
    # Needed to make minimum timezone aware
    minimum_datetime = datetime.min.replace(tzinfo=pytz.UTC)
    datetime_now = datetime.now().replace(tzinfo=pytz.UTC)

    signed_off_restricted_studies = AssayRun.objects.filter(
        restricted=True
    ).exclude(
        signed_off_by_id=None
    )

    # Indicates whether there are required stakeholders that have not approved
    required_stakeholder_map = {}

    relevant_required_stakeholders_without_approval = AssayRunStakeholder.objects.filter(
        sign_off_required=True,
        signed_off_by_id=None,
        study__id__in=signed_off_restricted_studies
    )

    for stakeholder in relevant_required_stakeholders_without_approval:
        required_stakeholder_map.update({
            stakeholder.study_id: True
        })

    # Contains as a datetime the lastest approval for a study
    latest_approval = {}

    approved_stakeholders = AssayRunStakeholder.objects.filter(
        sign_off_required=True,
        study__id__in=signed_off_restricted_studies
    ).exclude(
        signed_off_by_id=None
    )

    for stakeholder in approved_stakeholders:
        # Compare to minimum if no date at the moment
        if stakeholder.signed_off_date > latest_approval.get(stakeholder.study_id, minimum_datetime):
            latest_approval.update({
                stakeholder.study_id: stakeholder.signed_off_date
            })

    for study in signed_off_restricted_studies:
        # If there are no stakeholders, just use the sign off date
        if study.id not in latest_approval:
            # Days are approximated for a year
            greater_than_a_year_ago = study.signed_off_date < datetime_now - timedelta(days=365.2425)
        else:
            # Days are approximated for a year
            greater_than_a_year_ago = latest_approval.get(study.id) < datetime_now - timedelta(days=365.2425)

        stakeholders_without_approval = required_stakeholder_map.get(study.id, False)

        # Publish the study if no stakeholders without approval AND it was sent to Level to greater than a year ago
        if not stakeholders_without_approval and greater_than_a_year_ago:
            # print study, 'has been published'
            study.restricted = False
            study.save()

            superusers_to_be_alerted = User.objects.filter(is_superuser=True, is_active=True)

            # Magic strings are in poor taste, should use a template instead
            superuser_subject = 'Study Automatically Made Public: {0}'.format(study)
            superuser_message = render_to_string(
                'assays/email/superuser_study_made_public_alert.txt',
                {
                    'study': study,
                }
            )

            for user_to_be_alerted in superusers_to_be_alerted:
                user_to_be_alerted.email_user(superuser_subject, superuser_message, DEFAULT_FROM_EMAIL)
