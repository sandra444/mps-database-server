import json
from django.http import HttpResponse


def webhook(request):
    if "refs/heads/master" in request.POST.ref:
        data = {'status': 'ok'}
    else:
        data = {'status': 'bad'}
    return HttpResponse(json.dumps(data), content_type="application/json")


def database(request):
    data = {'status': 'ok'}
    return HttpResponse(json.dumps(data), content_type="application/json")
