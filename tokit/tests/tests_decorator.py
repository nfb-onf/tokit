# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import simplejson

from tokit.decorators import validate_token
from tokit.models import Token, TokenPermission

class Dummy(object) :
    pass

class DecoratorsTest(TestCase) :
    #/Users/sjolicoeur/Dev/nfb_tube2/nfb_api/decorators/__init__.py
    def setUp(self):
        self.key_owner = User(username="api_user")
        self.key_owner.save()
        self.api_key = Token(key="101010", owner=self.key_owner)
        self.api_key.access_count_last_day = 0
        self.api_key.save()
        self.api_key.permissions.add(TokenPermission.objects.get(codename='can_get_from_api'))
        self.api_key.permissions.add(TokenPermission.objects.get(codename='can_post_to_api'))
        
    def tearDown(self):
        self.api_key.delete()
        self.key_owner.delete()
        
    def test_decorated_function_should_pass_with_valid_key(self) :
        self.api_key.is_valid = True       
        self.api_key.is_internal = True
        self.api_key.save()
        @validate_token(permissions=['can_post_to_api', 'can_get_from_api'])
        def silly_fun(req) :
            return "success"
        request = Dummy()
        request.POST = { "api_key" : self.api_key.key }
        request.method = "POST"
        print silly_fun(request)
        assert silly_fun(request) == "success", "Key was found to be invalid"

    def test_decorated_function_should_fail_if_key_dont_have_permission_assign(self) :
        token = Token(key="101011", owner=self.key_owner)
        token.is_valid = True
        token.save()
        @validate_token(permissions=['can_post_to_api'])
        def silly_fun(req) :
            return "success"
        request = Dummy()
        request.POST = {"api_key" : token.key }
        request.method = "POST"
        result = silly_fun(request)
        self.assertEqual(result.content, """{"msg": "Error this key does not have the permission to access this call", "status": -997, "API_KEY": "101011", "method": "POST"}""")
        token.delete()
    
    def test_decorated_function_should_fail_with_invalid_key_POST(self) :
        self.api_key.is_valid = False
        self.api_key.is_internal = True
        self.api_key.save()
        @validate_token(permissions=['can_post_to_api', 'can_get_from_api'])
        def silly_fun(req) :
            return "success"
        request = Dummy()
        request.POST = {"api_key" : self.api_key.key }
        request.method = "POST"
        result = silly_fun(request)
        assert result.content == """{"msg": "Error INVALID API Key used please use or register a proper key", "status": -999, "API_KEY": "101010", "method": "POST"}""", "Key was found to be invalid"

    def test_decorated_function_should_fail_with_invalid_key_GET(self):
        self.api_key.is_valid = False
        self.api_key.is_internal = False
        @validate_token()
        def silly_fun(req) :
            return "success"
        request = Dummy()
        request.GET = {"api_key" : 'bob' }
        request.method = "GET"
        result = silly_fun(request)
        assert result.content == """{"msg": "Error INVALID API Key used please use or register a proper key", "status": -999, "API_KEY": "bob", "method": "GET"}""", "Expected the key to check as False"
        
    def test_decorated_function_should_valid_token_quota_is_over_limit_and_should_check_false(self):
        self.api_key.is_valid = True
        self.api_key.access_count_last_day = 1000000
        self.api_key.save()
        @validate_token()
        def silly_fun(req) :
            return "success"
        request = Dummy()
        request.GET = {"api_key" : self.api_key.key }
        request.method = "GET"
        result = silly_fun(request)
        self.assertEqual(result.content, """{"msg": "Error quota exceeded!", "status": -800, "API_KEY": "101010", "method": "GET"}""")
        
    def test_valid_token_over_its_limit_that_is_internal_should_check_true(self):
        self.api_key.is_valid = True
        self.api_key.access_count_last_day = 1000000
        self.api_key.is_internal = True
        self.api_key.save()
        @validate_token()
        def silly_fun(req) :
            return "success"
        request = Dummy()
        request.GET = {"api_key" : self.api_key.key }
        request.method = "GET"
        result = silly_fun(request)
        self.assertEqual(result, 'success')
