from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from .eventsink import sink
from .clean import dbclean

@csrf_exempt
def eventsink(request):
    try:
        sink(request)
        return HttpResponse()
    except:
        return HttpResponse(status=500)

def cleandb(request):
    response = HttpResponse(
        json.dumps(dbclean(request)), content_type="application/json"
    )

    return response
