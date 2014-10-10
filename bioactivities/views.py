# coding=utf-8

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from bioactivities.models import *
from bioactivities.parsers import *
from bioactivities.serializers import BioactivitiesSerializer

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


@csrf_exempt
def bioactivities_list(request):
    """
    List all code snippets, or create a new Bioactivity.
    """
    if request.method == 'GET':
        # data = Bioactivity.objects.all().select_related("compound")
        data = Bioactivity.objects.raw(
            'SELECT id,compound_id,bioactivity_type,value,'
            'units FROM  bioactivities_bioactivity;'
        )

        serializer = BioactivitiesSerializer(data, many=True)
        return JSONResponse(serializer.data)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = BioactivitiesSerializer(data=data)
        if serializer.is_valid():
            # serializer.save()    # do not save anything yet
            return JSONResponse(serializer.data, status=201)
        return JSONResponse(serializer.errors, status=400)


@csrf_exempt
def bioactivities_detail(request, pk):
    """
    Retrieve, update or delete a Bioactivity.
    """
    try:
        snippet = Bioactivity.objects.get(pk=pk)
    except Bioactivity.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = BioactivitiesSerializer(snippet)
        return JSONResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = BioactivitiesSerializer(snippet, data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data)
        return JSONResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        snippet.delete()
        return HttpResponse(status=204)


@csrf_exempt
def list_of_all_bioactivities_in_bioactivities(request):
    return JSONResponse(generate_list_of_all_bioactivities_in_bioactivities())


@csrf_exempt
def list_of_all_targets_in_bioactivities(request):

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

    return JSONResponse(generate_list_of_all_targets_in_bioactivities(desired_organisms, desired_target_types))


@csrf_exempt
def list_of_all_compounds_in_bioactivities(request):
    return JSONResponse(generate_list_of_all_compounds_in_bioactivities())

@csrf_exempt
def list_of_all_data_in_bioactivities(request):
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

    return JSONResponse(generate_list_of_all_data_in_bioactivities(desired_organisms, desired_target_types))

@csrf_exempt
def gen_heatmap(request):
    result = heatmap(request)
    if result:
        logging.debug('Final JSON response step: returning JSON response'
                      ' with heatmap result')
        return JSONResponse(result)
    else:
        logging.debug('Final JSON response step failed: result has no data')
        return HttpResponse()
