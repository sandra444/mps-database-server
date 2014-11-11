from .models import Compound

from django.views.generic import ListView, DetailView


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
