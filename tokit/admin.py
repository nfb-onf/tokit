# -*- coding: utf-8 -*-
# Copyright (c) 2011, National Film Board of Canada - Office National du Film du Canada

from django.contrib import admin

from tokit.models import Token, TokenPermission

class TokenAdmin(admin.ModelAdmin):
    list_display = ('key','description','access_count','request_per_day_limit','is_valid', 'is_internal')
    list_filter = ['is_valid','is_internal','date_created','last_modfied']
    search_fields = ['key', 'description']
admin.site.register(Token,TokenAdmin)


class TokenPermissionAdmin(admin.ModelAdmin):
    pass
admin.site.register(TokenPermission, TokenPermissionAdmin)
