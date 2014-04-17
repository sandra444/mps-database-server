from django.http import HttpResponse


def main(request):
    return HttpResponse(open("angularjs/mps.html"))
