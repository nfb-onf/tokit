# -*- coding: utf-8 -*-
# Copyright (c) 2011, National Film Board of Canada - Office National du Film du Canada

from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.test.client import Client
from django.conf import settings
from django.http import HttpRequest

from tokit.models import Token
from tokit.key_manager import extract_api_key

class TokenModelTest(TestCase):
    fixtures = ['tokit/fixtures/initial_data.json']
    def setUp(self):
        self.c = Client()
        self.key_owner = User(username="api_user")
        self.key_owner.save()
        self.token = Token(description='test key valid', owner=self.key_owner, is_valid=True)
        self.key_invalid = Token(description='test key invalid', owner=self.key_owner)
        self.token.save()
        self.key_invalid.save()
        self.request = HttpRequest()
        
    def tearDown(self):
        self.key_owner.delete()

    def test_extract_api_key_should_return_a_key_when_set_in_header(self):
        self.assertEqual(extract_api_key(self.request), None)
        self.request.META['HTTP_API_KEY'] = 12345
        self.assertEqual(extract_api_key(self.request), 12345)

    def test_extract_api_key_should_return_the_key_from_the_querystring_for_get(self):
        self.request.method = "GET"
        self.request.GET['api_key'] = 12345
        self.assertEqual(extract_api_key(self.request), 12345)
        
    def test_extract_api_key_should_return_the_key_from_the_querystring_for_post(self):
        self.request.method = "POST"
        self.request.POST['api_key'] = 12345
        self.assertEqual(extract_api_key(self.request), 12345)
