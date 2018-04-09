from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from .forms import SearchForm

from haystack.query import SearchQuerySet
from haystack.views import search_view_factory
import haystack.forms

from django.contrib.auth.models import Group

import os

from mps.settings import MEDIA_ROOT

from resources.models import Definition
from django.views.generic.base import TemplateView

from microdevices.models import MicrophysiologyCenter
from mps.templatetags.custom_filters import ADMIN_SUFFIX, VIEWER_SUFFIX


def main(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            return search(request)

    else:
        form = SearchForm(initial={'app': 'Global'})

    c = RequestContext(request)

    c.update({
        'form': form,
    })

    return render_to_response('index.html', c)


def loggedin(request):
    c = RequestContext(request)
    c.update({'full_name': request.user.username})
    return render_to_response('loggedin.html', c)


def search(request):
    app = request.POST.get('app', '')
    search_term = request.POST.get('search_term', '')

    bioactivities = {
        'compound': request.POST.get('compound', ''),
        'target': request.POST.get('target', ''),
        'name': request.POST.get('name', ''),
        'pubchem': request.POST.get('pubchem', ''),
        'exclude_targetless': request.POST.get('exclude_targetless', ''),
        'exclude_organismless': request.POST.get('exclude_organismless', ''),
        'exclude_questionable': request.POST.get('exclude_questionable', ''),
    }

    # If there is not a specified app, just return to the home page
    if not app:
        return HttpResponseRedirect('/')

    if app == 'Global':
        return HttpResponseRedirect(u'/search?q={}'.format(search_term))

    elif app == 'Bioactivities':
        search_term = [(term + '=' + bioactivities.get(term)) for term in bioactivities if bioactivities.get(term)]
        search_term = '&'.join(search_term)
        return HttpResponseRedirect(u'/bioactivities/?{}'.format(search_term))

    # If, for whatever reason, invalid data is entered, just return to the home page
    else:
        return HttpResponseRedirect('/')

# class CustomSearch(SearchView):
#
#     results_per_page = 1000
#
#     def get_results(self):
#         """
#         NORMALLY Fetches the results via the form.
#         Returns an empty list if there's no query to search with.
#         """
#         if self.query:
#             return SearchQuerySet().autocomplete(text=self.query)
#         else:
#             return []
#
#     def extra_context(self):
#         spelling = self.results.spelling_suggestion(self.query)
#         return {'suggestion': spelling,}


def get_search_queryset_with_permissions(request):
    sqs = SearchQuerySet().exclude(permissions='==PERMISSION START==')

    groups_with_center = MicrophysiologyCenter.objects.all().values_list('groups', flat=True)
    groups_with_center_full = {group.name: True for group in Group.objects.filter(id__in=groups_with_center)}

    if request.user.groups.all().count():
        user_groups = {
            group.name.replace(ADMIN_SUFFIX, '').replace(VIEWER_SUFFIX, ''): True for group in request.user.groups.all()
            if group.name.replace(ADMIN_SUFFIX, '').replace(VIEWER_SUFFIX, '') in groups_with_center_full
        }

        for group in user_groups.keys():
            sqs = sqs | SearchQuerySet().filter(permissions=group)

    return sqs


# A generic use of the search_view_factory
def custom_search(request):
    # Filter on group: either get all with no group or those with a group the user has
    sqs = get_search_queryset_with_permissions(request)

    view = search_view_factory(
        template='search/search.html',
        searchqueryset=sqs,
        form_class=haystack.forms.ModelSearchForm,
        results_per_page=1000,
    )

    return view(request)


def mps_help(request):
    c = RequestContext(request)
    # Add version for templates
    c['version'] = len(os.listdir(MEDIA_ROOT + '/excel_templates/'))
    # Get glossary
    c['glossary'] = Definition.objects.exclude(definition='')

    return render_to_response('help.html', c)


# TODO Consider defining this in URLS or either bringing the rest here
class UnderConstruction(TemplateView):
    template_name = 'under_construction.html'
