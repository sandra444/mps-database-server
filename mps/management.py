import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess


@csrf_exempt
def webhook(request):
    data = json.loads(request.body)

    try:
        if "refs/heads/master" in data.ref:
            if "nszceta" in data.pusher.name:
                subprocess.call(["touch", "~/touch-reload-production"])
                return HttpResponse(status=200)
    except KeyError:
        return HttpResponse(status=405)


@csrf_exempt
def database(request):
    data = {'status': 'ok'}
    return HttpResponse(json.dumps(data), content_type="application/json")
