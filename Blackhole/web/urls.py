# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from web.views import IndexTemplateView, AppUserCreateView, AppUserListView, ProfileCreateView, ProfileListView, ProfileDeleteView, ProfileUpdateView, HostDeleteView, HostUpdateView, HostListView, \
    HostCreateView, EnvironmentCreateView, EnvironmentListView, EnvironmentDeleteView, EnvironmentUpdateView, UserIdentityCreateView, UserIdentityListView, UserIdentityDeleteView, \
    UserIdentityUpdateView, AppUserDeleteView, PrivateKeyUpdateView, PrivateKeyDeleteView, PrivateKeyListView, PrivateKeyCreateView, HostConnectionUpdateView, HostConnectionDeleteView, \
    HostConnectionListView, HostConnectionCreateView, AdminUserCreateView, AdminUserListView, AdminUserUpdateView, GroupCreateView, GroupUpdateView, GroupListView, GroupDeleteView, get_sessions, \
    ActiveSessionTemplateView, download_session_log, FindSessionLogsFormView, AppUserUpdateView, \
    DBCreateView, DBListView, DBDeleteView, DBUpdateView, DBConnectionCreateView, DBConnectionListView, \
    DBConnectionDeleteView, DBConnectionUpdateView, kill_session

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'blackhole.views.home', name='home'),
    url(r'^$', IndexTemplateView.as_view(), name='home'),
    url(r'^app_user/create$', AppUserCreateView.as_view(), name='app_user_create'),
    url(r'^app_user/$', AppUserListView.as_view(), name='app_user_list'),
    url(r'^app_user/delete/(?P<pk>\d+)/$', AppUserDeleteView.as_view(), name='app_user_delete'),
    url(r'^app_user/update/(?P<pk>\d+)/$', AppUserUpdateView.as_view(), name='app_user_update'),
    url(r'^profile/create$', ProfileCreateView.as_view(), name='profile_create'),
    url(r'^profile/$', ProfileListView.as_view(), name='profile_list'),
    url(r'^profile/delete/(?P<pk>\d+)/$', ProfileDeleteView.as_view(), name='profile_delete'),
    url(r'^profile/update/(?P<pk>\d+)/$', ProfileUpdateView.as_view(), name='profile_update'),
    url(r'^host/create$', HostCreateView.as_view(), name='host_create'),
    url(r'^host/$', HostListView.as_view(), name='host_list'),
    url(r'^host/delete/(?P<pk>\d+)/$', HostDeleteView.as_view(), name='host_delete'),
    url(r'^host/update/(?P<pk>\d+)/$', HostUpdateView.as_view(), name='host_update'),
    url(r'^db/create$', DBCreateView.as_view(), name='db_create'),
    url(r'^db/$', DBListView.as_view(), name='db_list'),
    url(r'^db/delete/(?P<pk>\d+)/$', DBDeleteView.as_view(), name='db_delete'),
    url(r'^db/update/(?P<pk>\d+)/$', DBUpdateView.as_view(), name='db_update'),
    url(r'^environment/create$', EnvironmentCreateView.as_view(), name='environment_create'),
    url(r'^environment/$', EnvironmentListView.as_view(), name='environment_list'),
    url(r'^environment/delete/(?P<pk>\d+)/$', EnvironmentDeleteView.as_view(), name='environment_delete'),
    url(r'^environment/update/(?P<pk>\d+)/$', EnvironmentUpdateView.as_view(), name='environment_update'),
    url(r'^user_identity/create$', UserIdentityCreateView.as_view(), name='user_identity_create'),
    url(r'^user_identity/$', UserIdentityListView.as_view(), name='user_identity_list'),
    url(r'^user_identity/delete/(?P<pk>\d+)/$', UserIdentityDeleteView.as_view(), name='user_identity_delete'),
    url(r'^user_identity/update/(?P<pk>\d+)/$', UserIdentityUpdateView.as_view(), name='user_identity_update'),
    url(r'^privatekey/create$', PrivateKeyCreateView.as_view(), name='privatekey_create'),
    url(r'^privatekey/$', PrivateKeyListView.as_view(), name='privatekey_list'),
    url(r'^privatekey/delete/(?P<pk>\d+)/$', PrivateKeyDeleteView.as_view(), name='privatekey_delete'),
    url(r'^privatekey/update/(?P<pk>\d+)/$', PrivateKeyUpdateView.as_view(), name='privatekey_update'),
    url(r'^host_connection/create$', HostConnectionCreateView.as_view(), name='hostConnection_create'),
    url(r'^host_connection/$', HostConnectionListView.as_view(), name='hostConnection_list'),
    url(r'^host_connection/delete/(?P<pk>\d+)/$', HostConnectionDeleteView.as_view(), name='hostConnection_delete'),
    url(r'^host_connection/update/(?P<pk>\d+)/$', HostConnectionUpdateView.as_view(), name='hostConnection_update'),
    url(r'^db_connection/create$', DBConnectionCreateView.as_view(), name='dbConnection_create'),
    url(r'^db_connection/$', DBConnectionListView.as_view(), name='dbConnection_list'),
    url(r'^db_connection/delete/(?P<pk>\d+)/$', DBConnectionDeleteView.as_view(), name='dbConnection_delete'),
    url(r'^db_connection/update/(?P<pk>\d+)/$', DBConnectionUpdateView.as_view(), name='dbConnection_update'),

    #Admin
    url(r'^admin_user/create$', AdminUserCreateView.as_view(), name='admin_user_create'),
    url(r'^admin_user/$', AdminUserListView.as_view(), name='admin_user_list'),
    #url(r'^admin_user/delete/(?P<pk>\d+)/$', AppUserDeleteView.as_view(), name='admin_user_delete'),
    url(r'^admin_user/update/(?P<pk>\d+)/$', AdminUserUpdateView.as_view(), name='admin_user_update'),
    url(r'^group/create$', GroupCreateView.as_view(), name='group_create'),
    url(r'^group/update/(?P<pk>\d+)/$', GroupUpdateView.as_view(), name='group_update'),
    url(r'^group/delete/(?P<pk>\d+)/$', GroupDeleteView.as_view(), name='group_delete'),
    url(r'^group/$', GroupListView.as_view(), name='group_list'),
    url(r'^session_log/search$', FindSessionLogsFormView.as_view(), name='find_sessionlog'),
    #Template View
    url(r'^sessions/get_active$', ActiveSessionTemplateView.as_view(), name='active_sessions'),
    #url(r'^sessions/session_log/(?P<pk>\d+)$', SessionLogDetailView.as_view(), name='session_log_view'),
    #web services
    url(r'^services/get_sessions$', get_sessions, name='get_sessions_ws'),
    url(r'^services/kill_session$', kill_session, name='kill_session_ws'),
    #function view
    url(r'^services/session_log/download/(?P<pk>\d+)$', download_session_log, name='download_session_log'),
    url(r'^selectable/', include('selectable.urls'))
)

