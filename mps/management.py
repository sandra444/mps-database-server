import json
import subprocess
import hmac
import hashlib

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def webhook(request):
    try:
        data = json.loads(request.body)
        # use our hidden credential file to import username and
        # password info
        import mps_credentials

        remote_signature = request.META.get('HTTP_X_HUB_SIGNATURE').split('=')[
            1]
        real_signature = hmac.new(
            mps_credentials.webhook_secret,
            request.body,
            hashlib.sha1
        ).hexdigest()

        if remote_signature not in real_signature:
            raise Exception

        # we only want to update if we push to master
        if "refs/heads/master" in data['ref']:

            # adam is responsible for deploying to master
            if "nszceta" in data['pusher']['name']:
                subprocess.call(
                    ['/home/mps/mps-database-server/scripts/reload-all.sh']
                )
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
