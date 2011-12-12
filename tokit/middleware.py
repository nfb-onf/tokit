# -*- coding: utf-8 -*-
# Copyright (c) 2011, National Film Board of Canada - Office National du Film du Canada

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.utils import simplejson

from tokit.models import Token, TokitPath


def get_api_key(aKey) :
    try :
        token = Token.objects.get( key = aKey, is_valid=True )
        return token
    except Token.DoesNotExist :
        return None

def extract_api_key(request):
    if request.META.get("HTTP_API_KEY") : # HTTP is dynamicaly added by django !@#$$!
        return request.META.get("HTTP_API_KEY")
    method = getattr(request, request.method)
    if method.get("api_key") :
        return method.get("api_key")
    return None


class APIAuthMiddleware(object):
    def process_request(self, request):
        if not TokitPath.is_key_required_for(request.path):
            return None

        request_api_key = extract_api_key(request)
        if request_api_key :
            key = get_api_key(request_api_key)
            if key and key.has_access() :
                return None

        return HttpResponse("Forbidden", status = 401)
