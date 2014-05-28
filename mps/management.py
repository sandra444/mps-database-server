import json
from django.http import HttpResponse


def webhook(request):
    pass


def database(request):

    data = {'status': 'ok'}
    return HttpResponse(json.dumps(data), content_type="application/json")
