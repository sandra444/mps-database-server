# TODO PLEASE AVOID WILDCARD IMPORTS
from mps.templatetags.custom_filters import has_group, is_group_viewer, is_group_editor, is_group_admin
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.template import RequestContext, loader
from django.http import HttpResponseForbidden
from assays.models import AssayRun
from mps.templatetags.custom_filters import filter_groups


def PermissionDenied(request, message):
    """This function will take a string a render 403.html with that string as context"""
    template = loader.get_template('403.html')
    context = RequestContext(request, {
        'message': message
    })
    return HttpResponseForbidden(template.render(context))


# def check_if_user_is_active(user):
#     if not user or not user.is_active:
#         return PermissionDenied(
#             self.request,
#             'Your account is not currently active<br>'
#             'If you have recently registered, be sure to check your email for the activation link<br>'
#             'If you suspect this is an error, please contact an administrator'
#         )
#     else:
#         return None


def user_is_active(user):
    """Checks whether the user is active"""
    return user.is_active


# Add this mixin via multiple-inheritance and you need not change the dispatch every time
class LoginRequiredMixin(object):
    """This mixin requires the user to log in before continuing"""
    @method_decorator(login_required)
    @method_decorator(user_passes_test(user_is_active))
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class OneGroupRequiredMixin(object):
    """This mixin requires the user to have at least one group"""
    @method_decorator(login_required)
    @method_decorator(user_passes_test(user_is_active))
    def dispatch(self, *args, **kwargs):
        # if self.request.user.groups.all().count() == 0:
        #     return PermissionDenied(self.request, 'You must be a member of at least one group')
        valid_groups = filter_groups(self.request.user)
        if not valid_groups:
            return PermissionDenied(self.request, 'You must be a member of at least one group')
        return super(OneGroupRequiredMixin, self).dispatch(*args, **kwargs)


class ObjectGroupRequiredMixin(object):
    """This mixin requires group matching object's bound group"""
    @method_decorator(login_required)
    @method_decorator(user_passes_test(user_is_active))
    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        if not is_group_editor(self.request.user, self.object.group.name):
            return PermissionDenied(self.request, 'You must be a member of the group ' + str(self.object.group))
        if self.object.signed_off_by:
            return PermissionDenied(
                self.request,
                'You cannot edit this because it has been signed off on by {0} {1}.'
                ' If something needs to be changed, contact the individual who signed off.'
                ' If you are the individual who signed off, please contact a database administrator.'.format(
                    self.object.signed_off_by.first_name,
                    self.object.signed_off_by.last_name
                )
            )
        return super(ObjectGroupRequiredMixin, self).dispatch(*args, **kwargs)


class StudyGroupRequiredMixin(object):
    """This mixin requires the user to have the group matching the study's group

    Attributes:
    cloning_permitted - Specifies whether cloning is permitted
    detail - indicates that a detail page was initially requested
    update_redirect_url - where to to redirect in the case of detail redirect
    """
    # Default value for whether or not cloning is permitted
    cloning_permitted = False
    detail = False
    # Default value for url to redirect to
    update_redirect_url = 'update/'

    @method_decorator(login_required)
    @method_decorator(user_passes_test(user_is_active))
    def dispatch(self, *args, **kwargs):
        if self.kwargs.get('study_id', ''):
            study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])

            if not is_group_editor(self.request.user, study.group.name):
                return PermissionDenied(self.request, 'You must be a member of the group ' + str(study.group))

            # Do we want this behavior??
            if study.signed_off_by:
                return PermissionDenied(
                    self.request,
                    'You cannot add this because the study has been signed off on by {0} {1}.'
                    ' If something needs to be changed, contact the individual who signed off.'
                    ' If you are the individual who signed off, please contact a database administrator.'.format(
                        study.signed_off_by.first_name,
                        study.signed_off_by.last_name
                    )
                )

            if self.cloning_permitted and self.request.GET.get('clone', ''):
                clone = get_object_or_404(self.model, pk=self.request.GET.get('clone', ''))
                if not is_group_editor(self.request.user, clone.group.name):
                    return PermissionDenied(
                        self.request,
                        'You must be a member of the group ' + str(clone.group) + ' to clone this'
                    )
        else:
            try:
                current_object = self.get_object()
            except:
                # Evil except here!
                return PermissionDenied(self.request, 'An error has occurred.')
            current_type = str(type(current_object))
            if current_type == "<class 'assays.models.AssayChipSetup'>":
                study = current_object.assay_run_id
            elif current_type == "<class 'assays.models.AssayPlateSetup'>":
                study = current_object.assay_run_id
            elif current_type == "<class 'assays.models.AssayChipReadout'>":
                study = current_object.chip_setup.assay_run_id
            elif current_type == "<class 'assays.models.AssayPlateReadout'>":
                study = current_object.setup.assay_run_id
            elif current_type == "<class 'assays.models.AssayChipTestResult'>":
                study = current_object.chip_readout.chip_setup.assay_run_id
            elif current_type == "<class 'assays.models.AssayPlateTestResult'>":
                study = current_object.readout.setup.assay_run_id

            if is_group_editor(self.request.user, study.group.name) and not study.signed_off_by:
                # Redirects either to url + update or the specified url + object ID (as an attribute)
                # This is a little tricky if you don't look for {} in update_redirect_url
                if self.detail:
                    return redirect(self.update_redirect_url.format(current_object.id))
                else:
                    return super(StudyGroupRequiredMixin, self).dispatch(*args, **kwargs)

            # If the object is not restricted and the user is NOT a listed viewer
            elif study.restricted and not is_group_viewer(self.request.user, study.group.name):
                return PermissionDenied(self.request, 'You must be a member of the group ' + str(study.group))

            if study.signed_off_by and not self.detail:
                return PermissionDenied(
                    self.request,
                    'You cannot modify this because the study has been signed off on by {0} {1}.'
                    ' If something needs to be changed, contact the individual who signed off.'
                    ' If you are the individual who signed off, please contact a database administrator.'.format(
                        study.signed_off_by.first_name,
                        study.signed_off_by.last_name
                    )
                )

            # Otherwise return the detail view
            if self.detail:
                return super(StudyGroupRequiredMixin, self).dispatch(*args, **kwargs)
            else:
                return PermissionDenied(self.request, 'You do not have permission to edit this.')

        return super(StudyGroupRequiredMixin, self).dispatch(*args, **kwargs)


class ViewershipMixin(object):
    """This mixin checks if the user has the group neccessary to at least view the entry
    
    Attributes:
    study - specifies what study to look to for permissions
    """
    # Default study as None
    study = None

    @method_decorator(login_required)
    @method_decorator(user_passes_test(user_is_active))
    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        if self.study.access == 'editors' and not has_group(self.request.user, self.study.group.name):
            return PermissionDenied(
                self.request,
                'You do not have editor permissions for the group ' + str(self.study.group)
            )
        elif not self.study.access == 'public' and not is_group_viewer(self.request.user, self.study.group.name):
            return PermissionDenied(
                self.request,
                'You do not have viewer permissions for the group ' + str(self.study.group)
            )
        # Otherwise return the detail view
        return super(ViewershipMixin, self).dispatch(*args, **kwargs)


# TODO ADD STUDY HERE (cannot refer straight to .object.restricted)
# WIP
class DetailRedirectMixin(object):
    """This mixin checks if the user has the object's group, if so it redirects to the edit page

    If the user does not have the correct group, it redirects to the details page

    Attributes:
    update_redirect_url - where to redirect it update is possible
    study - specifies what study to look to for permissions
    """
    # Default value for url to redirect to
    update_redirect_url = 'update/'
    # Default study as None
    study = None

    @method_decorator(login_required)
    @method_decorator(user_passes_test(user_is_active))
    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        # If user CAN edit the item, redirect to the respective edit page
        # If the item is signed off on, it is no longer editable
        if is_group_editor(self.request.user, self.object.group.name) and not self.object.signed_off_by:
            # Redirects either to url + update or the specified url + object ID (as an attribute)
            # This is a little tricky if you don't look for {} in update_redirect_url
            return redirect(self.update_redirect_url.format(self.object.id))
        # If the object is restricted and the user is NOT a listed viewer
        elif self.study.access == 'editors' and not has_group(self.request.user, self.study.group.name):
            return PermissionDenied(
                self.request,
                'You do not have editor permissions for the group ' + str(self.study.group)
            )
        elif not self.study.access == 'public' and not is_group_viewer(self.request.user, self.study.group.name):
            return PermissionDenied(
                self.request,
                'You do not have viewer permissions for the group ' + str(self.study.group)
            )
        # Otherwise return the detail view
        return super(DetailRedirectMixin, self).dispatch(*args, **kwargs)


# NOT CURRENTLY USED
# Require user to be the creator or a group admin
class CreatorOrAdminRequiredMixin(object):
    """This mixin requires the user to be the creator of the object"""
    @method_decorator(login_required)
    @method_decorator(user_passes_test(user_is_active))
    # Deny access if not the CREATOR
    # Note the call for request.user.is_authenticated
    # Interestingly, Django wraps request.user until it is accessed
    # Thus, to perform this comparison it is necessary to access request.user via authentication
    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        if not self.request.user.is_authenticated() or (self.request.user != self.object.created_by and not is_group_admin(self.request.user, self.object.group.name)):
            return PermissionDenied(self.request, 'You can only delete entries that you have created')
        return super(CreatorOrAdminRequiredMixin, self).dispatch(*args, **kwargs)


# Require user to be a group admin
class AdminRequiredMixin(object):
    """This mixin requires the user to be a group admin"""

    @method_decorator(login_required)
    @method_decorator(user_passes_test(user_is_active))
    # Deny access if not the CREATOR
    # Note the call for request.user.is_authenticated
    # Interestingly, Django wraps request.user until it is accessed
    # Thus, to perform this comparison it is necessary to access request.user via authentication
    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        if not is_group_admin(self.request.user, self.object.group.name):
            return PermissionDenied(self.request, 'Only group admins can delete entries. Please contact your group admin.')
        return super(AdminRequiredMixin, self).dispatch(*args, **kwargs)


# Require the specified group or fail
class SpecificGroupRequiredMixin(object):
    """This mixin requires the user to have a specific group

    PLEASE NOTE: you must add the attribute 'required_group_name' to the view in question
    """
    @method_decorator(login_required)
    @method_decorator(user_passes_test(user_is_active))
    def dispatch(self, *args, **kwargs):
        if has_group(self.request.user, self.required_group_name):
            return super(SpecificGroupRequiredMixin, self).dispatch(*args, **kwargs)
        else:
            return PermissionDenied(
                self.request,
                'Contact an administrator if you would like to gain permission'
            )
