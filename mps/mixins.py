from mps.templatetags.custom_filters import *
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.template import RequestContext, loader
from django.http import HttpResponseForbidden
from assays.models import AssayRun
from django.contrib.auth.models import Group

# This function will take a string a render 403.html with that string as context
def PermissionDenied(request, message):
    template = loader.get_template('403.html')
    context = RequestContext(request, {
        'message': message
    })
    return HttpResponseForbidden(template.render(context))

# Add this mixin via multiple-inheritance and you need not change the dispatch every time
# Only require log in
class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


#Require the user to have at least one group
class OneGroupRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if len(self.request.user.groups.values_list('pk', flat=True)) == 0:
            return PermissionDenied(self.request,'You must be a member of at least one group')
        return super(OneGroupRequiredMixin, self).dispatch(*args, **kwargs)


# Require group matching object's bound group
# Note that this theoretically might not be accurate if someone meddled around in the admin
class ObjectGroupRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        if not has_group(self.request.user, self.object.group):
            return PermissionDenied(self.request,'You must be a member of the group ' + str(self.object.group))
        return super(ObjectGroupRequiredMixin, self).dispatch(*args, **kwargs)


# Require group matching study
class StudyGroupRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        study = get_object_or_404(AssayRun, pk=self.kwargs['study_id'])
        if not has_group(self.request.user, study.group):
            return PermissionDenied(self.request,'You must be a member of the group ' + str(study.group))
        return super(StudyGroupRequiredMixin, self).dispatch(*args, **kwargs)


# WIP
# Detail redirect mixin
class DetailRedirectMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        # If user CAN edit the item, redirect to the respective edit page
        if has_group(self.request.user, self.object.group):
            return redirect('update/')
        elif self.object.restricted:
            return PermissionDenied(self.request,'You must be a member of the group ' + str(self.object.group))
        return super(DetailRedirectMixin, self).dispatch(*args, **kwargs)


# Require user to be creator
class CreatorRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        # Deny access if not the CREATOR
        # Note the call for request.user.is_authenticated
        # Interestingly, Django wraps request.user until it is accessed
        # Thus, to perform this comparison it is necessary to access request.user via authentication
        if not self.request.user.is_authenticated() or self.request.user != self.object.created_by:
            return PermissionDenied(self.request,'You can only delete entries that you have created')
        return super(CreatorRequiredMixin, self).dispatch(*args, **kwargs)


# Require the specified group or fail
class SpecificGroupRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        group = Group.objects.get(name=self.required_group_name)
        if has_group(self.request.user, group):
            return super(SpecificGroupRequiredMixin, self).dispatch(*args, **kwargs)
        else:
            return PermissionDenied(
                self.request,
                'You do not have permission to view this page <br>'
                'Contact an administrator if you would like to gain permission'
            )
