from django.http import HttpResponse
import os
import settings

def main(request):
    return HttpResponse(open(os.path.join(settings.STATIC_ROOT, 'mps.html')))
