from .models import Compound
from django.views.generic import ListView, DetailView, CreateView
# from django.utils.decorators import method_decorator
# from django.contrib.auth.decorators import login_required
from mps.mixins import OneGroupRequiredMixin
from compounds.forms import CompoundForm


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

    def get_context_data(self, **kwargs):
        compounds = list(Compound.objects.all().order_by('name').values_list('id', flat=True))
        current = compounds.index(int(self.kwargs.get('pk')))

        if current == 0:
            previous = compounds[-1]
        else:
            previous = compounds[current - 1]
        if current == len(compounds)-1:
            next = compounds[0]
        else:
            next = compounds[current + 1]

        context = super(CompoundsDetail, self).get_context_data(**kwargs)

        context.update({'previous':previous, 'next':next})
        return context


class CompoundsAdd(OneGroupRequiredMixin, CreateView):
    form_class = CompoundForm
    template_name = 'compounds/compounds_add.html'

    # # Custom dispatch (achieve same as GET in assay views
    # @method_decorator(login_required)
    # def dispatch(self, request, *args, **kwargs):
    #     if len(request.user.groups.values_list('pk',flat=True)) == 0:
    #         return PermissionDenied(request,'You must be a member of at least one group')
    #     return super(CompoundsAdd, self).dispatch(request, *args, **kwargs)
