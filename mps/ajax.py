# NOTE: Decided it was best to keep AJAX calls app-separated
import ujson as json
from django.http import *
import logging
logger = logging.getLogger(__name__)

from django.contrib.auth.models import Group

from haystack.query import SearchQuerySet


# Default
def main(request):
    return HttpResponseServerError()


def fetch_global_search_suggestions(request):
    data = []

    # Get text from request
    text = request.POST.get('text')

    # Filter on group: either get all with no group or those with a group the user has
    sqs = SearchQuerySet().exclude(group__in=Group.objects.all())

    if request.user and request.user.groups.all():
          sqs = sqs | SearchQuerySet().filter(group__in=request.user.groups.all())

    suggestions = sqs.autocomplete(text=text)
    # At the moment, I just take the first five results
    for suggestion in suggestions[:10]:
        #data.append(suggestion.suggestion)
        data.append({
            'label': suggestion.text.split('\n')[0],
            'value': suggestion.text.split('\n')[1]
        })

    return HttpResponse(json.dumps(data),
                        content_type="application/json")

switch = {
    'fetch_global_search_suggestions': fetch_global_search_suggestions,
}


def ajax(request):
    post_call = request.POST.get('call')

    if not post_call:
        logger.error('post_call not present in request to ajax')
        return HttpResponseServerError

    # Abort if there is no valid call sent to us from Javascript
    if not post_call:
        return main(request)

    # Route the request to the correct handler function
    # and pass request to the functions
    try:
        # select the function from the dictionary
        procedure = switch[post_call]

    # If all else fails, handle the error message
    except KeyError:
        return main(request)

    else:
        # execute the function
        return procedure(request)
