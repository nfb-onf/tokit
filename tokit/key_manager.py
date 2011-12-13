# -*- coding: utf-8 -*-
# Copyright (c) 2011, National Film Board of Canada - Office National du Film du Canada

from tokit.models import Token

def get_api_key(aKey) :
    try :
        token = Token.objects.get( key = aKey, is_valid=True )
        return token
    except Token.DoesNotExist :
        return None

def extract_api_key(request):
    if hasattr(request, "META"):
        if request.META.get("HTTP_API_KEY") : # HTTP is dynamicaly added by django !@#$$!
            return request.META.get("HTTP_API_KEY")
    method = getattr(request, request.method)
    if method.get("api_key") :
        return method.get("api_key")
    return None
