# coding=utf-8

from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.template import RequestContext

from rest_framework.renderers import JSONRenderer
#from rest_framework.parsers import JSONParser

#import ujson as json

#from bioactivities.models import *
from bioactivities.parsers import *
# from bioactivities.serializers import BioactivitiesSerializer

from mps.views import SearchForm, search

import logging
logger = logging.getLogger(__name__)


class JSONResponse(HttpResponse):

    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        """

        :rtype : object
        """
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def bioactivities_list(request):
    """
    Retrieve a list of Bioactivities
    """
    if request.method == 'GET':
        compound = request.GET.get('compound', '')
        target = request.GET.get('target', '')
        name = request.GET.get('name', '')
        pubchem = request.GET.get('pubchem', '')
        exclude_targetless = request.GET.get('exclude_targetless', '')
        exclude_organismless = request.GET.get('exclude_organismless', '')
        exclude_questionable = request.GET.get('exclude_questionable', '')

        # I might want to sort by multiple fields later
        if any([compound, target, name]):
            if pubchem:
                data = PubChemBioactivity.objects.all().select_related(
                    'compound__name',
                    'assay__target',
                    'assay__pubchem_id'
                )
            else:
                data = Bioactivity.objects.exclude(
                    standard_name='',
                    standardized_units='',
                    standardized_value__isnull=True
                ).select_related(
                    'compound__name',
                    'target__name',
                    'assay__chemblid'
                )

            if compound:
                data = data.filter(compound__name__icontains=compound)

            if target:
                if pubchem:
                    data = data.filter(assay__target__name__icontains=target)
                else:
                    data = data.filter(target__name__icontains=target)

            if name:
                if pubchem:
                    data = data.filter(activity_name__icontains=name)
                else:
                    data = data.filter(standard_name__icontains=name)

            if exclude_targetless:
                # Exclude where target is "Unchecked"
                if pubchem:
                    data = data.filter(
                        assay__target__isnull=False
                    ).exclude(assay__target__name="Unchecked").exclude(assay__target__name='')
                else:
                    data = data.filter(
                       target__isnull=False
                    ).exclude(target__name="Unchecked").exclude(target__name='')

            if exclude_organismless:
                # Exclude where assay and target organism are null
                # TODO JUST SAVE THE TARGET ORGANISM AS THE ASSAY ORGANISM?
                data = data.exclude(assay__organism='').exclude(assay__target__organism='')
                # Exclude where organism is "Unspecified"
                data = data.exclude(assay__organism="Unspecified").exclude(assay__target__organism="Unspecified")

            if exclude_questionable:
                data = data.filter(data_validity='')

            length = data.count()

            # Limit at 5000
            bioactivities = data[:5000]

            c = RequestContext(request)
            c.update({
                'bioactivities': bioactivities,
                'compound': compound,
                'target': target,
                'name': name,
                'length': length,
                'pubchem': pubchem
            })

            return render_to_response('bioactivities/bioactivities_list.html', c)

        else:
            raise Http404

    else:
        raise Http404

# Old API
# @csrf_exempt
# def bioactivities_list(request):
#     """
#     List all code snippets, or create a new Bioactivity.
#     """
#     if request.method == 'GET':
#         # data = Bioactivity.objects.all().select_related("compound")
#         data = Bioactivity.objects.raw(
#             'SELECT id,compound_id,bioactivity_type,value,'
#             'units FROM  bioactivities_bioactivity;'
#         )
#
#         serializer = BioactivitiesSerializer(data, many=True)
#         return JSONResponse(serializer.data)
#
#     elif request.method == 'POST':
#         data = JSONParser().parse(request)
#         serializer = BioactivitiesSerializer(data=data)
#         if serializer.is_valid():
#             # serializer.save()    # do not save anything yet
#             return JSONResponse(serializer.data, status=201)
#         return JSONResponse(serializer.errors, status=400)
#
#
# @csrf_exempt
# def bioactivities_detail(request, pk):
#     """
#     Retrieve, update or delete a Bioactivity.
#     """
#     try:
#         snippet = Bioactivity.objects.get(pk=pk)
#     except Bioactivity.DoesNotExist:
#         return HttpResponse(status=404)
#
#     if request.method == 'GET':
#         serializer = BioactivitiesSerializer(snippet)
#         return JSONResponse(serializer.data)
#
#     elif request.method == 'PUT':
#         data = JSONParser().parse(request)
#         serializer = BioactivitiesSerializer(snippet, data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return JSONResponse(serializer.data)
#         return JSONResponse(serializer.errors, status=400)
#
#     elif request.method == 'DELETE':
#         snippet.delete()
#         return HttpResponse(status=204)


# TODO NEEDS REVISION
@csrf_exempt
def list_of_all_bioactivities_in_bioactivities(request):
    return JSONResponse(generate_list_of_all_bioactivities_in_bioactivities(True))


@csrf_exempt
def list_of_all_targets_in_bioactivities(request):
    exclude_questionable = json.loads(request.GET.get('exclude_questionable'))
    pubchem = json.loads(request.GET.get('pubchem'))
    target_types = json.loads(request.GET.get('target_types'))
    organisms = json.loads(request.GET.get('organisms'))

    desired_target_types = [
        x.get(
            'name'
        ) for x in target_types
        if x.get(
            'is_selected'
        ) is True
    ]

    desired_organisms = [
        x.get(
            'name'
        ) for x in organisms
        if x.get(
            'is_selected'
        ) is True
    ]

    return JSONResponse(
        generate_list_of_all_targets_in_bioactivities(
            exclude_questionable,
            pubchem,
            desired_organisms,
            desired_target_types
        )
    )


@csrf_exempt
def list_of_all_compounds_in_bioactivities(request):
    exclude_questionable = json.loads(request.GET.get('exclude_questionable'))
    pubchem = json.loads(request.GET.get('pubchem'))

    return JSONResponse(generate_list_of_all_compounds_in_bioactivities(
        exclude_questionable,
        pubchem,
    ))


@csrf_exempt
def list_of_all_data_in_bioactivities(request):
    exclude_questionable = json.loads(request.GET.get('exclude_questionable'))
    pubchem = json.loads(request.GET.get('pubchem'))
    target_types = json.loads(request.GET.get('target_types'))
    organisms = json.loads(request.GET.get('organisms'))

    desired_target_types = [
        x.get(
            'name'
        ) for x in target_types
        if x.get(
            'is_selected'
        ) is True
    ]

    desired_organisms = [
        x.get(
            'name'
        ) for x in organisms
        if x.get(
            'is_selected'
        ) is True
    ]

    return JSONResponse(
        generate_list_of_all_data_in_bioactivities(
            exclude_questionable,
            pubchem,
            desired_organisms,
            desired_target_types
        )
    )


@csrf_exempt
def gen_heatmap(request):
    result = heatmap(request)
    if result:
        # logging.debug('Final JSON response step: returning JSON response'
        #               ' with heatmap result')
        return JSONResponse(result)
    else:
        logging.debug('Final JSON response step failed: result has no data')
        return HttpResponse()


@csrf_exempt
def gen_cluster(request):
    result = cluster(request)
    if result:
        # logging.debug('Final JSON response step: returning JSON response'
        #               ' with heatmap result')
        return JSONResponse(result)
    else:
        logging.debug('Final JSON response step failed: result has no data')
        return HttpResponse()


@csrf_exempt
def gen_table(request):
    result = table(request)
    if result:
        # logging.debug('Final JSON response step: returning JSON response'
        #               ' with heatmap result')
        return JSONResponse(result)
    else:
        logging.debug('Final JSON response step failed: result has no data')
        return HttpResponse()


def view_cluster(request):
    c = RequestContext(request)
    return render_to_response('bioactivities/cluster.html', c)


def view_heatmap(request):
    c = RequestContext(request)
    return render_to_response('bioactivities/heatmap.html', c)


def view_table(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            return search(request)

    else:
        form = SearchForm(initial={'app': 'Bioactivities'})

    c = RequestContext(request)

    c.update({
        'form': form,
    })

    return render_to_response('bioactivities/table.html', c)


def view_model(request):
    c = RequestContext(request)
    return render_to_response('bioactivities/model.html', c)
