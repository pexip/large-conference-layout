from django.http import HttpResponse
import json
import logging
from .policy import service_config, location, avatar, directory, registration


def service_configuration(request):
    logging.info(request)
    response = HttpResponse(
        json.dumps(service_config(request)), content_type="application/json"
    )

    return response


def participant_location(request):
    logging.info(request)
    response = HttpResponse(
        json.dumps(location(request)), content_type="application/json"
    )

    return response


def participant_avatar(request, alias):
    logging.info(request)
    logging.info(alias)
 
    response = HttpResponse(
        avatar(request, alias), content_type="image/jpeg"
    )
    response['Content-Disposition'] = 'attachment; filename="avatar.jpg"'
    
    return response


def registration_directory(request):
    logging.info(request)
    response = HttpResponse(
        json.dumps(directory(request)), content_type="application/json"
    )

    return response


def registration_alias(request, alias):
    logging.info(request)
    logging.info(alias)
    response = HttpResponse(
        json.dumps(registration(request, alias)), content_type="application/json"
    )

    return response
