# -*- coding: utf-8 -*-
# Copyright (c) 2011, National Film Board of Canada - Office National du Film du Canada

__author__="Stephane Jolicoeur-Fidelia (s.jolicoeur@nfb.ca)"
__date__="24 janvier 2011"

from django.http import HttpResponse
from django.utils import simplejson

from tokit.models import Token

def generate_json_error_msg(status, msg, key, method):
    return simplejson.dumps({
                    "msg" : msg,
                    "status" : status,
                    'API_KEY' : key,
                    'method' : method,
                })

def get_api_key(aKey) :
    try :
        token = Token.objects.get( key = aKey, is_valid=True )
        return token
    except Token.DoesNotExist :
        return None

def validate_token(permissions=[]) :
    def validate_decorator(func):
        def wrapper(request, *args, **kwargs) :
            if request.method == "POST" :
                API_key = request.POST.get("api_key", None)
            else :
                API_key = request.GET.get("api_key", None)
            key = get_api_key(API_key)
            
            if not key :
                json = generate_json_error_msg(-999
                    ,"Error INVALID API Key used please use or register a proper key"
                    ,API_key
                    ,request.method
                    )
                return HttpResponse(json, mimetype='application/json')

            if key.has_all_permissions(permissions) and key.has_access():
                return func( request, *args, **kwargs)

            if not key.has_all_permissions(permissions):
                json = generate_json_error_msg(-997
                    ,"Error this key does not have the permission to access this call"
                    ,API_key
                    ,request.method
                    )
            if not key.has_access():
                json = generate_json_error_msg(-800
                    ,"Error quota exceeded!"
                    ,API_key
                    ,request.method
                    )                
            return HttpResponse(json, mimetype='application/json')
                            
        return wrapper
    return validate_decorator
