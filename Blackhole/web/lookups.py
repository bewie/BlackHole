# -*- coding: utf-8 -*-
from selectable.base import ModelLookup
from selectable.registry import registry
from web.models import AppUser, Host, Database, Profile, HostConnection, DBConnection, Environment, PrivateKey
from selectable.decorators import login_required


@login_required
class AppUserLookup(ModelLookup):
    model = AppUser
    search_fields = ('first_name__icontains', 'last_name__icontains', 'username__icontains')
    #filters = {'enabled': True, }

    def get_item_value(self, item):
        # Display for currently selected item
        return item.username

    def get_item_label(self, item):
        # Display for choice listings
        return item.get_full_name()

@login_required
class HostLookup(ModelLookup):
    model = Host
    search_fields = ('name__icontains', 'ip__icontains')

    def get_item_value(self, item):
        # Display for currently selected item
        return item.name

    def get_item_label(self, item):
        # Display for choice listings
        return item.name

@login_required
class DBLookup(ModelLookup):
    model = Database
    search_fields = ('name__icontains', 'ip__icontains')

    def get_item_value(self, item):
        # Display for currently selected item
        return item.name

    def get_item_label(self, item):
        # Display for choice listings
        return item.name

@login_required
class ProfileLookup(ModelLookup):
    model = Profile
    search_fields = ('name__icontains',)

    def get_item_value(self, item):
        # Display for currently selected item
        return item.name

    def get_item_label(self, item):
        # Display for choice listings
        return item.name


@login_required
class HostConnectionLookup(ModelLookup):
    model = HostConnection
    search_fields = ('host__name__icontains',)

    def get_item_value(self, item):
        # Display for currently selected item
        return item.host.name

    def get_item_label(self, item):
        # Display for choice listings
        return "%s as %s" % (item.host.name, item.authentication_user)

@login_required
class DBConnectionLookup(ModelLookup):
    model = DBConnection
    search_fields = ('host__name__icontains',)

    def get_item_value(self, item):
        # Display for currently selected item
        return item.host.name

    def get_item_label(self, item):
        # Display for choice listings
        return "%s as %s" % (item.host.name, item.authentication_user)

@login_required
class EnvironmentLookup(ModelLookup):
    model = Environment
    search_fields = ('name__icontains', 'description__icontains')

    def get_item_value(self, item):
        # Display for currently selected item
        return item.description

    def get_item_label(self, item):
        # Display for choice listings
        return "%s - %s" % (item.name, item.description)

@login_required
class PrivateKeyLookup(ModelLookup):
    model = PrivateKey
    search_fields = ('user__icontains', 'environment__name__icontains', 'environment__description__icontains')

    def get_item_value(self, item):
        # Display for currently selected item
        return item.user

    def get_item_label(self, item):
        # Display for choice listings
        return "%s - %s" % (item.user, item.environment)


registry.register(AppUserLookup)
registry.register(HostLookup)
registry.register(DBLookup)
registry.register(ProfileLookup)
registry.register(HostConnectionLookup)
registry.register(DBConnectionLookup)
registry.register(EnvironmentLookup)
registry.register(PrivateKeyLookup)