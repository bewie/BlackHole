# -*- coding: utf-8 -*-
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_syncdb
from web import models


def create_self_identification(sender, **kwargs):
    print "Creating self identification"
    models.UserIdentity.objects.get_or_create(username=models.SELF_IDENTIFICATION)
    print " Creating Groups"
    if not Group.objects.filter(name='Admin'):
        admin_group_permissions = ['add_group', 'change_group', 'delete_group', 'add_user', 'change_user', 'delete_user',
                                   'add_environment', 'change_environment', 'delete_environment', 'add_host', 'change_host',
                                   'delete_host', 'add_useridentity', 'change_useridentity', 'delete_useridentity',
                                   'add_privatekey', 'change_privatekey', 'delete_privatekey', 'add_hostconnection',
                                   'change_hostconnection', 'delete_hostconnection', 'add_profile', 'change_profile',
                                   'delete_profile', 'add_appuser', 'change_appuser', 'delete_appuser']
        admin_group = Group(name='Admin')
        admin_group.save()
        for permission in admin_group_permissions:
            admin_group.permissions.add(Permission.objects.get(codename=permission))
        admin_group.save()

post_syncdb.connect(create_self_identification, sender=models)
