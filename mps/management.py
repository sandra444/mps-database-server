import json
import subprocess

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def webhook(request):
    try:
        data = json.loads(request.body)
    except ValueError:
        return HttpResponse(status=405)
    try:
        if "refs/heads/master" in data['ref']:
            if "nszceta" in data['pusher']['name']:
                subprocess.call(["touch", "~/touch-reload-production"])
                return HttpResponse(status=200)
    except KeyError:
        pass
    return HttpResponse(status=405)


@csrf_exempt
def database(request):
    data = json.loads(request.body)
    try:
        if "upddi" in data.data:
            return HttpResponse(
                subprocess.check_output(
                    ["pg_dump", "-Fc", "mpsdb"]
                )
            )
    except KeyError:
        pass
    return HttpResponse(status=405)
