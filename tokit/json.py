# -*- coding: utf-8 -*-

import datetime
import decimal

from django.http import HttpResponse
from django.db.models.query import QuerySet, EmptyQuerySet
from django.db import models
from django.utils import datetime_safe
from django.core import serializers
from django.utils import simplejson       
from django.core.serializers.json import DjangoJSONEncoder
from django import forms

__all__ = ['NFBDjangoJSONEncoder', 'JSONResponse', 'render_to_json']

class NFBDjangoJSONEncoder(simplejson.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time, models, querysets and decimal types.
    """

    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"

    def default(self, o):
        if isinstance(o, datetime.datetime):
            d = datetime_safe.new_datetime(o)
            return d.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT))
        elif isinstance(o, datetime.date):
            d = datetime_safe.new_date(o)
            return d.strftime(self.DATE_FORMAT)
        elif isinstance(o, datetime.time):
            return o.strftime(self.TIME_FORMAT)
        elif isinstance(o, decimal.Decimal):
            return str(o)
        elif isinstance(o, QuerySet) and o.count() == 0:
            return str('[]')
        elif isinstance(o, QuerySet):
            return serializers.serialize("json", o)
        elif isinstance(o, EmptyQuerySet):
            return list(o)
        elif isinstance(o, models.Model) :
            return serializers.serialize("json", [o])[1:-1] # do this to remove the brackets! from the serialisation hack
        elif isinstance(o, forms.Form) :
            return "None"
        else:
            return super(NFBDjangoJSONEncoder, self).default(o)

    @staticmethod
    def render_as_json(data):
        return simplejson.dumps(data, cls=NFBDjangoJSONEncoder)
    


class JSONResponse(HttpResponse):
    """ 
    A simple `HttpResponse` subclass which returns JSON objects.
    """
    default_media_type = 'text/javascript'

    def __init__(self, content='', mimetype=None, status=None,
        content_type=None):
        if not mimetype: 
            mimetype = self.default_media_type
        HttpResponse.__init__(self, content, mimetype)
        self.content = content

    def tojson(self, instance):
        """ encode `instance` into a JSON object """
        self.content = demjson.encode(instance)

def render_to_json(request, obj):
    """ Shortcut function for returning a JSON object """
    json_response = JSONResponse()
    try:
        json_response.tojson(obj)
    except demjson.JSONEncodeError:
        raise
    else:
        return json_response


