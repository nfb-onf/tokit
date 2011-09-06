#import urllib
import uuid
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

TOKIT_DB = getattr(settings, "TOKIT_DB", "default")

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
