import json
import subprocess

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def webhook(request):
    try:
        data = json.loads(request.body)
        source_ip = request.META['REMOTE_ADDR'].split('.')

        # if the request isn't from Github, forget it.
        if ('192' not in source_ip[0]) \
                and ('30' not in source_ip[1]) \
                and ('252' not in source_ip[2]):
            raise ValueError

        # we only want to update if we push to master
        if "refs/heads/master" in data['ref']:

            # adam is responsible for deploying to master
            if "nszceta" in data['pusher']['name']:
                subprocess.call(['git', 'reset', '--hard', 'HEAD'])
                subprocess.call(['git', 'fetch'])
                subprocess.call(['git', 'pull'])
                subprocess.call(['git', 'reset', '--hard', 'HEAD'])
                subprocess.call(['touch', '/home/mps/touch-reload-production'])
                return HttpResponse(status=200)

    except KeyError:
        pass
    except ValueError:
        pass

    # if anything goes wrong, return 'method not allowed' code 405
    return HttpResponse(status=405)


@csrf_exempt
def database(request):
    return HttpResponse(
        subprocess.check_output(
            ["pg_dump", "-Fc", "mpsdb"]
        )
    )
