#-=- encoding: utf-8 -=-

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from tokit.models import Token, TokenPermission

class TokenModelTest(TestCase):
    def setUp(self):
        self.key_owner = User(username="api_user")
        self.key_owner.save()
        self.token = Token(description='test key valid', owner=self.key_owner, is_valid=True)
        self.key_invalid = Token(description='test key invalid', owner=self.key_owner)
        self.token.save()
        self.key_invalid.save()

    def tearDown(self):
        self.key_invalid.delete()
        self.token.delete()
        self.key_owner.delete()

    def test_token_should_be_able_to_generate_unique_key_on_creation(self):
        key = Token(description='test key', owner=self.key_owner)
        key.save()
        self.assertFalse(key.key in ['',0 ])
        key.delete()

    def test_is_key_valid_should_return_true_if_the_key_exist_and_is_valid(self):
        self.assertTrue(Token.objects.is_key_valid(self.token.key))
        self.assertFalse(Token.objects.is_key_valid(self.key_invalid.key))
        self.assertFalse(Token.objects.is_key_valid('asdfa-asdf-ads'))

    def test_get_permissions_should_return_a_list_of_permissions_the_token_has_set(self):
        token = Token(description='test key valid', owner=self.key_owner, is_valid=True)
        token.save()
        token.permissions.add(TokenPermission.objects.get(codename='can_get_from_api'))
        self.assertEqual(['can_get_from_api'], token.get_permissions())

    def test_has_permission_should_return_a_boolean_specifying_if_the_key_has_the_requested_permission(self):
        token = Token(description='test key', owner=self.key_owner, is_valid=True)
        token.save()
        token.permissions.add(TokenPermission.objects.get(codename='can_get_from_api'))
        key_postandget = Token(description='test key', owner=self.key_owner, is_valid=True)
        key_postandget.save()
        key_postandget.permissions.add(TokenPermission.objects.get(codename='can_get_from_api'))
        key_postandget.permissions.add(TokenPermission.objects.get(codename='can_post_to_api'))

        self.assertTrue(token.has_permission('can_get_from_api'))
        self.assertFalse(token.has_permission('can_post_to_api'))
        self.assertTrue(key_postandget.has_permission('can_get_from_api'))
        self.assertTrue(key_postandget.has_permission('can_post_to_api'))
    
    def test_has_all_permissions_should_return_a_boolean_if_token_has_all_required_permissions(self):
        key_postandget = Token(description='test key', owner=self.key_owner, is_valid=True)
        key_postandget.save()
        key_postandget.permissions.add(TokenPermission.objects.get(codename='can_get_from_api'))
        key_postandget.permissions.add(TokenPermission.objects.get(codename='can_post_to_api'))
        permissions = ['can_get_from_api', 'can_post_to_api']
        permissions_false = ['can_vote_in_china', 'can_get_from_api']
        
        self.assertTrue(key_postandget.has_all_permissions(permissions))
        self.assertFalse(key_postandget.has_all_permissions(permissions_false))
        key_postandget.delete()

    def test_has_access_should_return_true_if_token_is_internal(self):
        self.token.is_internal = True
        self.assertTrue(self.token.has_access())
        
    def test_has_access_should_validate_if_token_exceeded_access_quota_and_is_not_internal(self):
        self.token.is_internal = False
        self.token.access_count_last_day = 1800
        self.assertTrue(self.token.has_access())
        self.token.access_count_last_day = 2200
        self.assertFalse(self.token.has_access())


class TokenPermissionModelTest(TestCase):
    def test_fixture_load_correctly(self):
        try:
            get_perm = TokenPermission.objects.get(codename='can_get_from_api')
        except ObjectDoesNotExist:
            assert False, 'Get permission not set'
        
        try:
            post_perm = TokenPermission.objects.get(codename='can_post_to_api')
        except ObjectDoesNotExist:
            assert False, 'Post permission not insert'

	
