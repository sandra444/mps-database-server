from .models import Compound
from django.views.generic import ListView, DetailView, CreateView
# from django.utils.decorators import method_decorator
# from django.contrib.auth.decorators import login_required
from mps.mixins import OneGroupRequiredMixin
from .forms import CompoundForm


class CompoundsList(ListView):
    model = Compound
    template_name = 'compounds/compounds_list.html'
    # If variable pagination is desired, just jam that into GET too
    # paginate_by = 50
    #
    # def get_queryset(self):
    #     try:
    #         name = self.request.GET['name']
    #     except:
    #         name = ''
    #     if (name != ''):
    #         object_list = self.model.objects.filter(name__icontains = name)
    #     else:
    #         object_list = self.model.objects.all()
    #     return object_list

class CompoundsDetail(DetailView):
    model = Compound
    template_name = 'compounds/compounds_detail.html'


class CompoundsAdd(OneGroupRequiredMixin, CreateView):
    form_class = CompoundForm
    template_name = 'compounds/compounds_add.html'

    # # Custom dispatch (achieve same as GET in assay views
    # @method_decorator(login_required)
    # def dispatch(self, request, *args, **kwargs):
    #     if len(request.user.groups.values_list('pk',flat=True)) == 0:
    #         return PermissionDenied(request,'You must be a member of at least one group')
    #     return super(CompoundsAdd, self).dispatch(request, *args, **kwargs)


