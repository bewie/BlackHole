# -*- coding: utf-8 -*-
from django.contrib import admin
from django.forms import ModelForm, PasswordInput
from .models import Host, AppUser, Environment, UserIdentity, HostConnection, Profile, PrivateKey, SessionLog, \
    DBConnection, Database
from django.utils.translation import ugettext_lazy as _


class PasswordForm(ModelForm):
    class Meta:
        widgets = {
            'password': PasswordInput
        }

class PrivateKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'key_type', 'environment')
    search_fields = ['user']
    list_filter = ('user', 'environment')
    ordering = ['environment', 'user']


class UserAdmin(admin.ModelAdmin):
    actions = ['disable_users', 'enable_users']
    list_display = ('username', 'last_name', 'first_name', 'profile', 'enabled')
    search_fields = ['username', 'profile__name']
    list_filter = ('enabled', 'profile')
    filter_horizontal = ('allowed_environments',)
    ordering = ['profile__name', 'username']

    def disable_users(self, request, queryset):
        queryset.update(enabled=False)
    disable_users.short_description = _("Disable selected users")

    def enable_users(self, request, queryset):
        queryset.update(enabled=True)
    enable_users.short_description = _("Enable selected users")


class EnvironmentAdmin(admin.ModelAdmin):
    search_fields = ['description']


class HostConnectionAdmin(admin.ModelAdmin):
    list_display = ('host', 'authentication_user', 'authentication_method')
    list_filter = ('authentication_user', 'host__environment', 'authentication_method', 'host__os')
    search_fields = ['host__name']
    form = PasswordForm

class DBConnectionAdmin(admin.ModelAdmin):
    list_display = ('host', 'authentication_user')
    list_filter = ('authentication_user', 'host__environment', 'host__engine')
    search_fields = ['host__name']
    form = PasswordForm

class HostAdmin(admin.ModelAdmin):
    list_display = ('name', 'environment', 'description', 'ip', 'os')
    search_fields = ['name', 'ip']
    list_filter = ('environment',)
    ordering = ['environment']

class DatabaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'environment', 'description', 'ip', 'engine')
    search_fields = ['name', 'ip']
    list_filter = ('environment',)
    ordering = ['environment']

class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['name']
    filter_vertical = ('hosts', 'databases')
    ordering = ['name']


class UserIdentityAdmin(admin.ModelAdmin):
    search_fields = ['username']
    ordering = ['username']

admin.site.register(Host, HostAdmin)
admin.site.register(Database, DatabaseAdmin)
admin.site.register(AppUser, UserAdmin)
admin.site.register(Environment, EnvironmentAdmin)
admin.site.register(UserIdentity, UserIdentityAdmin)
admin.site.register(HostConnection, HostConnectionAdmin)
admin.site.register(DBConnection, DBConnectionAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(PrivateKey, PrivateKeyAdmin)
admin.site.register(SessionLog)
