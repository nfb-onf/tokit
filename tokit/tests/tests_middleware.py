# -*- coding: utf-8 -*-
# Copyright (c) 2011, National Film Board of Canada - Office National du Film du Canada

from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.test.client import Client
from django.conf import settings

from tokit.models import Token, TokitPath, TokenPermission, GlobalPathException, SpecificPathValidation

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

    def create_paths(self):
        GlobalPathException(path="/admin/").save()
        
    def tearDown(self):
        self.clear_paths()
        del self.c

    def clear_paths(self):
        map(lambda x: x.delete(), GlobalPathException.objects.all())
        map(lambda x: x.delete(), SpecificPathValidation.objects.all())

    def test_has_active_should_return_true_if_at_least_one_path_is_record(self):
        self.assertTrue(GlobalPathException.objects.is_active())
        self.assertFalse(SpecificPathValidation.objects.is_active())

    def test_tokit_path_should_not_let_adding_new_globalexception_when_the_is_specificPathValidation(self):
        SpecificPathValidation(path="/events").save()
        self.assertEqual(SpecificPathValidation.objects.all().count(), 1)
        print('all blobal path : %s' % GlobalPathException.objects.all())
        self.assertEqual(GlobalPathException.objects.all().count(), 1)
        self.clear_paths()
        SpecificPathValidation(path="/events").save()
        GlobalPathException(path="/admin/").save()
        self.assertEqual(SpecificPathValidation.objects.all().count(), 1)
        self.assertEqual(GlobalPathException.objects.all().count(), 0)
          
    def test_middleware_should_let_access_path_that_were_set_unprotected(self):
        GlobalPathException(path="/crossdomain.xml").save()
        admin = self.c.get("/admin/")
        self.assertEqual(admin.status_code, 200)
        admin_subpath = self.c.get("/admin/users/")
        self.assertEqual(admin_subpath.status_code, 200)
        restricted_path = self.c.get("/events/")
        self.assertEqual(restricted_path.status_code, 401)
        
    def test_middleware_should_let_access_path_under_the_one_define_only(self):
        self.clear_paths()
        GlobalPathException(path="/admin/users").save()
        admin = self.c.get("/admin/")
        # should also failed if cache isnt working correctly
        self.assertEqual(admin.status_code, 401)
        admin_subpath = self.c.get("/admin/users/")
        self.assertEqual(admin_subpath.status_code, 200)

    def test_middleware_should_only_restricted_access_to_specified_path_when_SpecificPathValidation_is_active(self):
        self.clear_paths()
        SpecificPathValidation(path="/events").save()
        self.assertEqual(SpecificPathValidation.objects.all().count(), 1)
        admin_subpath = self.c.get("/admin/users/")
        self.assertEqual(admin_subpath.status_code, 200)
        restricted_path = self.c.get("/events/")
        self.assertEqual(restricted_path.status_code, 401)
