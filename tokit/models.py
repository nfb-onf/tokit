# -*- coding: utf-8 -*-
# Copyright (c) 2011, National Film Board of Canada - Office National du Film du Canada

import uuid
import datetime
from sets import Set

from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save, post_delete

TOKIT_DB = getattr(settings, "TOKIT_DB", "default")

class TokitPathManager(models.Manager):
    def is_active(self):
        return bool(self.all().count())

TOKITPATHDOC = """
    Manage security by token for the middleware
    
    It selects the appropriate business rule to validate if a path should be secured

    If there is at least one entry in GlobalPathException and none in SpecificPathValidation, the rule is to validate all but those set in that table.

    If there is at least one entry in SpecificPathValidation, the rule is to validate only those that table.

    By default it is set to validate all but /admin
    
    """

class TokitPath(models.Model):
    __doc__ = TOKITPATHDOC
    path = models.CharField(max_length=255
                               ,unique=True
                               ,help_text="")
    CACHE_KEYS = Set([])
    
    class Meta:
        abstract = True

    def __str__(self):
        return self.path
    
    def __unicode__(self):
        return unicode(self.__str__())
    
    @staticmethod
    def is_key_required_for(req_path):
        key = 'tokit_path_%s' % req_path.replace('/', "_")
        is_key_required = cache.get(key)
        if is_key_required != None:
            return is_key_required
        is_key_required = TokitPath.mode_manager().is_key_required_for(req_path)
        cache.set(key, is_key_required, 3600)
        TokitPath.CACHE_KEYS.update([key])
        return is_key_required

    @staticmethod
    def mode_manager():
        if SpecificPathValidation.objects.is_active():
            return SpecificPathValidation
        return GlobalPathException

    @staticmethod
    def is_path_recorded(req_path, orm_objects):
        for path in orm_objects.all():
            if req_path.startswith(str(path)):
                return True
        return False

def clean_tokit_path_cache(sender, instance, **kwargs):
    action = kwargs.get('action', 'post_save')
    map(lambda key: cache.delete(key), TokitPath.CACHE_KEYS)
    del TokitPath.CACHE_KEYS
    TokitPath.CACHE_KEYS = Set([])
        
class GlobalPathException(TokitPath):
    __doc__ = TOKITPATHDOC
    objects = TokitPathManager()

    @staticmethod
    def is_key_required_for(req_path):
        return not TokitPath.is_path_recorded(req_path, GlobalPathException.objects)
    
    def save(self):
        if SpecificPathValidation.objects.is_active():
            return None
        super(GlobalPathException, self).save()

class SpecificPathValidation(TokitPath):
    __doc__ = TOKITPATHDOC
    objects = TokitPathManager()

    @staticmethod
    def is_key_required_for(req_path):
        return TokitPath.is_path_recorded(req_path, SpecificPathValidation.objects)
        
    def save(self):
        super(SpecificPathValidation, self).save()
            
post_save.connect(clean_tokit_path_cache, sender=GlobalPathException)
post_save.connect(clean_tokit_path_cache, sender=SpecificPathValidation)
post_delete.connect(clean_tokit_path_cache, sender=GlobalPathException)
post_delete.connect(clean_tokit_path_cache, sender=SpecificPathValidation)

# ==== Token        
class TokenPermissionManager(models.Manager):
    def get_query_set(self):
        return super(TokenPermissionManager, self).get_query_set().using(TOKIT_DB)

class TokenPermission(models.Model):
    name = models.CharField(max_length=255,unique=True)
    codename = models.CharField(max_length=255,unique=True)
    objects = TokenPermissionManager()

    def __unicode__(self):
        return u'%s' % self.name

class TokenManager(models.Manager):
    def get_query_set(self):
        return super(TokenManager, self).get_query_set().using(TOKIT_DB)

    def is_key_valid(self, key):
        keys = self.filter(key=str(key), is_valid=True)
        if len(keys) > 0:
            return True
        return False

class Token(models.Model):
    key = models.CharField(max_length=255,unique=True, blank=True)
    description = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modfied = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User)
    is_internal= models.BooleanField(default=False)
    permissions = models.ManyToManyField(TokenPermission, blank=True, null=True)

    # Limits
    is_valid = models.BooleanField(default=False)
    request_per_day_limit  = models.IntegerField(default = 2000)

    # logging
    access_count = models.PositiveIntegerField(default=0)
    access_count_last_day = models.PositiveIntegerField(default=0)
    last_access = models.DateTimeField(auto_now_add=True)

    objects = TokenManager()

    def _is_quota_exceed(self):
        return self.request_per_day_limit >= self.access_count_last_day

    def has_access(self):
        if self.is_internal == True:
            return True
        return self._is_quota_exceed()

    def has_permission(self, permission):
        if permission in self.get_permissions():
            return True
        return False    

    def has_all_permissions(self, permissions):
        permission_count = 0
        for perm in permissions:
            if self.has_permission(perm):
                permission_count += 1
        return True if len(permissions) == permission_count else False

    def get_permissions(self):
        return [perm.codename for perm in self.permissions.all()]

    def generate_key(self) :
        seed = "nfb.ca/%s/%s/%s/%s/%s" %  ( self.owner.username
                                            ,self.owner.email
                                            ,self.description
                                            ,self.request_per_day_limit
                                            ,datetime.datetime.now())
        new_key = uuid.uuid5(uuid.NAMESPACE_URL, seed.encode('ascii')).__str__()
        return new_key

    def __str__(self):
        return "Token :  %s" % self.key

    def __unicode__(self):
        return u"Token :  %s" % self.key

    def save(self, *args, **kwargs) :
        if not(self.key) or self.key == "0" :
            self.key = self.generate_key()
        super(Token, self).save(*args, **kwargs)

    class Admin:
        save_on_top = True
        list_display = ('key','description','current_request_count','request_per_day_limit','valid','is_internal')
        list_filter = ['valid','is_internal','date_created','last_modfied']
        search_fields = ['key',]

    class Meta:
        permissions = (
            ("can_post_to_api", "Can post updated info to the API"),
            ("can_get_from_api", "Can get datat from the API"),
        )


class TokenAccessLogManager(models.Manager):
    def get_query_set(self):
        return super(TokenAccessLogManager, self).get_query_set().using(TOKIT_DB)
    
    def write_log_for_key(self, key):
        return False

class TokenAccessLog(models.Model):
    key = models.ForeignKey(Token)
    date_created = models.DateTimeField(auto_now_add=True)

    objects = TokenAccessLogManager()

    def __str__(self):
        return "API KEY :  %s was used %s times" % (self.key.__str__(), count)

    def __unicode__(self):
        return u"API KEY :  %s was used %s times" % (self.key.__str__(), count)


class ClassName(object):
    """
    """
    
    def __init__(self, ):
        """
        """
        
        
