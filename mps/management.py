import json
import subprocess
import hmac
import hashlib
import pprint

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def webhook(request):
    try:
        data = json.loads(request.body)
        # use our hidden credential file to import username and
        # password info
        import mps_credentials

        pprint.pprint(request.META)

        remote_signature = request.META.get('X-Hub-Signature')
        real_signature = hmac.new(
            mps_credentials.webhook_secret,
            request.body,
            hashlib.sha256
        ).hexdigest()

        print(remote_signature)
        print(real_signature)

        # we only want to update if we push to master
        if "refs/heads/master" in data['ref']:

            # adam is responsible for deploying to master
            if "nszceta" in data['pusher']['name']:
                subprocess.call(['git', 'reset', '--hard', 'HEAD'])
                subprocess.call(['git', 'fetch'])
                subprocess.call(['git', 'pull'])
                subprocess.call(['git', 'reset', '--hard', 'HEAD'])
                subprocess.call(
                    ['touch', '/home/mps/touch-reload-production'])
                return HttpResponse(status=200)

    # return HTTP error if _anything_ goes wrong whatsoever.
    except Exception:
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
