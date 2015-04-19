import StringIO
import os
import zipfile
import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.generic import TemplateView, CreateView, ListView, DeleteView, UpdateView, DetailView, FormView
import redis
from web.forms import AppUserForm, AppUserUpdateForm, HostConnectionForm, AdminUserForm, FindSessionLogsForm, AppUserSearchForm, \
    DBConnectionForm, HostSearchForm, DBSearchForm, ProfileSearchForm, HostConnectionSearchForm, DBConnectionSearchForm, EnvironmentSearchForm, PrivateKeySearchForm
from web.models import AppUser, Profile, Host, Environment, UserIdentity, PrivateKey, HostConnection, SessionLog, \
    Database, DBConnection
from blackhole import settings
import json


class IndexTemplateView(TemplateView):
    template_name = "web/index.html"

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(IndexTemplateView, self).dispatch(request, *args, **kwargs)


## Admin
class AdminUserCreateView(SuccessMessageMixin, CreateView):
    model = User
    template_name = "web/admin_user_form.html"
    form_class = UserCreationForm
    success_url = reverse_lazy('home')
    success_message = _("%(username)s was created successfully")

    @method_decorator(permission_required('auth.add_user'))
    def dispatch(self, request, *args, **kwargs):
        return super(AdminUserCreateView, self).dispatch(request, *args, **kwargs)


class AdminUserListView(ListView):
    model = User
    template_name = "web/admin_user_list.html"
    paginate_by = 30

    @method_decorator(permission_required('auth.add_user'))
    def dispatch(self, request, *args, **kwargs):
        return super(AdminUserListView, self).dispatch(request, *args, **kwargs)


class AdminUserUpdateView(SuccessMessageMixin, UpdateView):
    model = User
    form_class = AdminUserForm
    template_name = "web/admin_user_update_form.html"
    success_url = reverse_lazy('home')
    success_message = _("%(username)s was updated successfully")

    @method_decorator(permission_required('auth.change_user'))
    def dispatch(self, request, *args, **kwargs):
        return super(AdminUserUpdateView, self).dispatch(request, *args, **kwargs)


class GroupCreateView(SuccessMessageMixin, CreateView):
    model = Group
    template_name = "web/group_form.html"
    #form_class = UserCreationForm
    success_url = reverse_lazy('home')
    success_message = _("%(name)s was created successfully")

    @method_decorator(permission_required('auth.add_group'))
    def dispatch(self, request, *args, **kwargs):
        return super(GroupCreateView, self).dispatch(request, *args, **kwargs)


class GroupUpdateView(SuccessMessageMixin, UpdateView):
    model = Group
    template_name = "web/group_update_form.html"
    success_url = reverse_lazy('home')
    success_message = _("%(name)s was updated successfully")

    @method_decorator(permission_required('auth.change_group'))
    def dispatch(self, request, *args, **kwargs):
        return super(GroupUpdateView, self).dispatch(request, *args, **kwargs)


class GroupListView(ListView):
    model = Group
    template_name = "web/group_list.html"
    paginate_by = 30

    @method_decorator(permission_required('auth.add_group'))
    def dispatch(self, request, *args, **kwargs):
        return super(GroupListView, self).dispatch(request, *args, **kwargs)


class GroupDeleteView(DeleteView):
    model = Group
    success_url = reverse_lazy('group_list')
    template_name = "web/group_confirm_delete.html"

    @method_decorator(permission_required('auth.delete_group'))
    def dispatch(self, request, *args, **kwargs):
        return super(GroupDeleteView, self).dispatch(request, *args, **kwargs)


## AppUser
class AppUserCreateView(SuccessMessageMixin, CreateView):
    model = AppUser
    template_name = "web/app_user_form.html"
    form_class = AppUserForm
    success_url = reverse_lazy('home')
    success_message = _("%(username)s was created successfully")

    @method_decorator(permission_required('web.add_appuser'))
    def dispatch(self, request, *args, **kwargs):
        return super(AppUserCreateView, self).dispatch(request, *args, **kwargs)


class AppUserListView(ListView):
    model = AppUser
    template_name = "web/app_user_list.html"
    paginate_by = 30

    @method_decorator(permission_required('web.add_appuser'))
    def dispatch(self, request, *args, **kwargs):
        return super(AppUserListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AppUserListView, self).get_context_data(**kwargs)
        context['search_form'] = AppUserSearchForm()
        return context


class AppUserUpdateView(SuccessMessageMixin, UpdateView):
    model = AppUser
    form_class = AppUserUpdateForm
    template_name = "web/app_user_update_form.html"
    success_url = reverse_lazy('home')
    success_message = _("%(username)s was updated successfully")

    @method_decorator(permission_required('web.change_appuser'))
    def dispatch(self, request, *args, **kwargs):
        return super(AppUserUpdateView, self).dispatch(request, *args, **kwargs)


class AppUserDeleteView(DeleteView):
    model = AppUser
    success_url = reverse_lazy('app_user_list')
    template_name = "web/app_user_confirm_delete.html"

    @method_decorator(permission_required('web.delete_appuser'))
    def dispatch(self, request, *args, **kwargs):
        return super(AppUserDeleteView, self).dispatch(request, *args, **kwargs)


## Profile
class ProfileCreateView(SuccessMessageMixin, CreateView):
    model = Profile
    template_name = "web/profile_form.html"
    #form_class = UserForm
    success_url = reverse_lazy('home')
    success_message = _("%(name)s was created successfully")

    @method_decorator(permission_required('web.add_profile'))
    def dispatch(self, request, *args, **kwargs):
        return super(ProfileCreateView, self).dispatch(request, *args, **kwargs)


class ProfileUpdateView(SuccessMessageMixin, UpdateView):
    model = Profile
    template_name = "web/profile_update_form.html"
    success_url = reverse_lazy('home')
    success_message = _("%(name)s was updated successfully")

    @method_decorator(permission_required('web.change_profile'))
    def dispatch(self, request, *args, **kwargs):
        return super(ProfileUpdateView, self).dispatch(request, *args, **kwargs)


class ProfileListView(ListView):
    model = Profile
    template_name = "web/profile_list.html"
    paginate_by = 30

    @method_decorator(permission_required('web.add_profile'))
    def dispatch(self, request, *args, **kwargs):
        return super(ProfileListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProfileListView, self).get_context_data(**kwargs)
        context['search_form'] = ProfileSearchForm()
        return context


class ProfileDeleteView(DeleteView):
    model = Profile
    success_url = reverse_lazy('profile_list')
    template_name = "web/profile_confirm_delete.html"

    @method_decorator(permission_required('web.delete_profile'))
    def dispatch(self, request, *args, **kwargs):
        return super(ProfileDeleteView, self).dispatch(request, *args, **kwargs)


## Hosts
class HostCreateView(SuccessMessageMixin, CreateView):
    model = Host
    template_name = "web/host_form.html"
    success_url = reverse_lazy('home')
    success_message = _("%(name)s was created successfully")

    @method_decorator(permission_required('web.add_host'))
    def dispatch(self, request, *args, **kwargs):
        return super(HostCreateView, self).dispatch(request, *args, **kwargs)


class HostUpdateView(SuccessMessageMixin, UpdateView):
    model = Host
    template_name = "web/host_update_form.html"
    success_url = reverse_lazy('home')
    success_message = _("%(name)s was updated successfully")

    @method_decorator(permission_required('web.change_host'))
    def dispatch(self, request, *args, **kwargs):
        return super(HostUpdateView, self).dispatch(request, *args, **kwargs)


class HostListView(ListView):
    model = Host
    template_name = "web/host_list.html"
    paginate_by = 30

    @method_decorator(permission_required('web.add_host'))
    def dispatch(self, request, *args, **kwargs):
        return super(HostListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(HostListView, self).get_context_data(**kwargs)
        context['search_form'] = HostSearchForm()
        return context


class HostDeleteView(DeleteView):
    model = Host
    success_url = reverse_lazy('host_list')
    template_name = "web/host_confirm_delete.html"

    @method_decorator(permission_required('web.delete_host'))
    def dispatch(self, request, *args, **kwargs):
        return super(HostDeleteView, self).dispatch(request, *args, **kwargs)


## Databases
class DBCreateView(SuccessMessageMixin, CreateView):
    model = Database
    template_name = "web/db_form.html"
    success_url = reverse_lazy('home')
    success_message = _("%(name)s was created successfully")

    @method_decorator(permission_required('web.add_database'))
    def dispatch(self, request, *args, **kwargs):
        return super(DBCreateView, self).dispatch(request, *args, **kwargs)


class DBUpdateView(SuccessMessageMixin, UpdateView):
    model = Database
    template_name = "web/db_update_form.html"
    success_url = reverse_lazy('home')
    success_message = _("%(name)s was updated successfully")

    @method_decorator(permission_required('web.change_database'))
    def dispatch(self, request, *args, **kwargs):
        return super(DBUpdateView, self).dispatch(request, *args, **kwargs)


class DBListView(ListView):
    model = Database
    template_name = "web/db_list.html"
    paginate_by = 30

    @method_decorator(permission_required('web.add_database'))
    def dispatch(self, request, *args, **kwargs):
        return super(DBListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DBListView, self).get_context_data(**kwargs)
        context['search_form'] = DBSearchForm()
        return context


class DBDeleteView(DeleteView):
    model = Database
    success_url = reverse_lazy('db_list')
    template_name = "web/db_confirm_delete.html"

    @method_decorator(permission_required('web.delete_database'))
    def dispatch(self, request, *args, **kwargs):
        return super(DBDeleteView, self).dispatch(request, *args, **kwargs)


## Environment
class EnvironmentCreateView(SuccessMessageMixin, CreateView):
    model = Environment
    template_name = "web/environment_form.html"
    success_url = reverse_lazy('home')
    success_message = _("%(description)s was created successfully")

    @method_decorator(permission_required('web.add_environment'))
    def dispatch(self, request, *args, **kwargs):
        return super(EnvironmentCreateView, self).dispatch(request, *args, **kwargs)


class EnvironmentUpdateView(SuccessMessageMixin, UpdateView):
    model = Environment
    template_name = "web/environment_update_form.html"
    success_url = reverse_lazy('home')
    success_message = _("%(name)s was updated successfully")

    @method_decorator(permission_required('web.change_environment'))
    def dispatch(self, request, *args, **kwargs):
        return super(EnvironmentUpdateView, self).dispatch(request, *args, **kwargs)


class EnvironmentListView(ListView):
    model = Environment
    template_name = "web/environment_list.html"
    paginate_by = 30

    @method_decorator(permission_required('web.add_environment'))
    def dispatch(self, request, *args, **kwargs):
        return super(EnvironmentListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EnvironmentListView, self).get_context_data(**kwargs)
        context['search_form'] = EnvironmentSearchForm()
        return context


class EnvironmentDeleteView(DeleteView):
    model = Environment
    success_url = reverse_lazy('environment_list')
    template_name = "web/environment_confirm_delete.html"

    @method_decorator(permission_required('web.delete_environment'))
    def dispatch(self, request, *args, **kwargs):
        return super(EnvironmentDeleteView, self).dispatch(request, *args, **kwargs)


## UserIdentity
class UserIdentityCreateView(SuccessMessageMixin, CreateView):
    model = UserIdentity
    template_name = "web/user_identity_form.html"
    success_url = reverse_lazy('home')
    success_message = _("%(username)s was created successfully")

    @method_decorator(permission_required('web.add_useridentity'))
    def dispatch(self, request, *args, **kwargs):
        return super(UserIdentityCreateView, self).dispatch(request, *args, **kwargs)


class UserIdentityUpdateView(SuccessMessageMixin, UpdateView):
    model = UserIdentity
    template_name = "web/user_identity_update_form.html"
    success_url = reverse_lazy('home')
    success_message = _("%(username)s was updated successfully")

    @method_decorator(permission_required('web.change_useridentity'))
    def dispatch(self, request, *args, **kwargs):
        return super(UserIdentityUpdateView, self).dispatch(request, *args, **kwargs)


class UserIdentityListView(ListView):
    model = UserIdentity
    template_name = "web/user_identity_list.html"
    paginate_by = 30

    @method_decorator(permission_required('web.add_useridentity'))
    def dispatch(self, request, *args, **kwargs):
        return super(UserIdentityListView, self).dispatch(request, *args, **kwargs)


class UserIdentityDeleteView(DeleteView):
    model = UserIdentity
    success_url = reverse_lazy('user_identity_list')
    template_name = "web/user_identity_confirm_delete.html"

    @method_decorator(permission_required('web.delete_useridentity'))
    def dispatch(self, request, *args, **kwargs):
        return super(UserIdentityDeleteView, self).dispatch(request, *args, **kwargs)


## Private Key
class PrivateKeyCreateView(SuccessMessageMixin, CreateView):
    model = PrivateKey
    template_name = "web/privatekey_form.html"
    success_url = reverse_lazy('home')
    success_message = _("PrivateKey for %(user)s was created successfully")

    @method_decorator(permission_required('web.add_privatekey'))
    def dispatch(self, request, *args, **kwargs):
        return super(PrivateKeyCreateView, self).dispatch(request, *args, **kwargs)


class PrivateKeyUpdateView(SuccessMessageMixin, UpdateView):
    model = PrivateKey
    template_name = "web/privatekey_update_form.html"
    success_url = reverse_lazy('home')
    success_message = _("PrivateKey for %(user)s was updated successfully")

    @method_decorator(permission_required('web.change_privatekey'))
    def dispatch(self, request, *args, **kwargs):
        return super(PrivateKeyUpdateView, self).dispatch(request, *args, **kwargs)


class PrivateKeyListView(ListView):
    model = PrivateKey
    template_name = "web/privatekey_list.html"
    paginate_by = 30

    @method_decorator(permission_required('web.add_privatekey'))
    def dispatch(self, request, *args, **kwargs):
        return super(PrivateKeyListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PrivateKeyListView, self).get_context_data(**kwargs)
        context['search_form'] = PrivateKeySearchForm()
        return context


class PrivateKeyDeleteView(DeleteView):
    model = PrivateKey
    success_url = reverse_lazy('privatekey_list')
    template_name = "web/privatekey_confirm_delete.html"

    @method_decorator(permission_required('web.delete_privatekey'))
    def dispatch(self, request, *args, **kwargs):
        return super(PrivateKeyDeleteView, self).dispatch(request, *args, **kwargs)


## HostConnection
class HostConnectionCreateView(SuccessMessageMixin, CreateView):
    model = HostConnection
    template_name = "web/hostConnection_form.html"
    success_url = reverse_lazy('home')
    form_class = HostConnectionForm
    success_message = _("Host Connection for %(authentication_user)s to %(host)s was created successfully")

    @method_decorator(permission_required('web.add_hostconnection'))
    def dispatch(self, request, *args, **kwargs):
        return super(HostConnectionCreateView, self).dispatch(request, *args, **kwargs)


class HostConnectionUpdateView(SuccessMessageMixin, UpdateView):
    model = HostConnection
    template_name = "web/hostConnection_update_form.html"
    success_url = reverse_lazy('home')
    success_message = _("Host Connection for %(authentication_user)s to %(host)s was updated successfully")

    @method_decorator(permission_required('web.change_hostconnection'))
    def dispatch(self, request, *args, **kwargs):
        return super(HostConnectionUpdateView, self).dispatch(request, *args, **kwargs)


class HostConnectionListView(ListView):
    model = HostConnection
    template_name = "web/hostConnection_list.html"
    paginate_by = 30

    @method_decorator(permission_required('web.add_hostconnection'))
    def dispatch(self, request, *args, **kwargs):
        return super(HostConnectionListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(HostConnectionListView, self).get_context_data(**kwargs)
        context['search_form'] = HostConnectionSearchForm()
        return context


class HostConnectionDeleteView(DeleteView):
    model = HostConnection
    success_url = reverse_lazy('hostConnection_list')
    template_name = "web/hostConnection_confirm_delete.html"

    @method_decorator(permission_required('web.delete_dbconnection'))
    def dispatch(self, request, *args, **kwargs):
        return super(HostConnectionDeleteView, self).dispatch(request, *args, **kwargs)


## DBConnection
class DBConnectionCreateView(SuccessMessageMixin, CreateView):
    model = DBConnection
    template_name = "web/dbConnection_form.html"
    success_url = reverse_lazy('home')
    form_class = DBConnectionForm
    success_message = _(u"Database Connection for %(authentication_user)s to %(host)s was created successfully")

    @method_decorator(permission_required('web.add_dbconnection'))
    def dispatch(self, request, *args, **kwargs):
        return super(DBConnectionCreateView, self).dispatch(request, *args, **kwargs)


class DBConnectionUpdateView(SuccessMessageMixin, UpdateView):
    model = DBConnection
    template_name = "web/dbConnection_update_form.html"
    success_url = reverse_lazy('home')
    success_message = _(u"Database Connection for %(authentication_user)s to %(host)s was updated successfully")

    @method_decorator(permission_required('web.change_dbconnection'))
    def dispatch(self, request, *args, **kwargs):
        return super(DBConnectionUpdateView, self).dispatch(request, *args, **kwargs)


class DBConnectionListView(ListView):
    model = DBConnection
    template_name = "web/dbConnection_list.html"
    paginate_by = 30

    @method_decorator(permission_required('web.add_dbconnection'))
    def dispatch(self, request, *args, **kwargs):
        return super(DBConnectionListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DBConnectionListView, self).get_context_data(**kwargs)
        context['search_form'] = DBConnectionSearchForm()
        return context


class DBConnectionDeleteView(DeleteView):
    model = DBConnection
    success_url = reverse_lazy('dbConnection_list')
    template_name = "web/dbConnection_confirm_delete.html"

    @method_decorator(permission_required('web.delete_dbconnection'))
    def dispatch(self, request, *args, **kwargs):
        return super(DBConnectionDeleteView, self).dispatch(request, *args, **kwargs)


class FindSessionLogsFormView(FormView):
    form_class = FindSessionLogsForm
    template_name = 'web/find_session_log.html'

    def form_valid(self, form, **kwargs):
        user = form.cleaned_data['user']
        from_date = form.cleaned_data['from_date']
        to_date = form.cleaned_data['to_date']
        days = datetime.timedelta(days=1)
        session_logs = SessionLog.objects.filter(user=user, login_date__range=(from_date, to_date + days))
        for log in session_logs:
            if log.log_file:
                log.can_download_log = True
            else:
                log.can_download_log = False
        return render_to_response(self.template_name, {'session_logs': session_logs}, context_instance=RequestContext(self.request))


# web services
@permission_required('web.view_session_logs')
def kill_session(request):
    if request.is_ajax():
        session_id = int(request.POST['id'])
        session_log = SessionLog.objects.get(pk=session_id)
        session_log.logout_date = timezone.now()
        session_log.save()
        redis_server = redis.Redis(settings.redis_server)
        connections = redis_server.smembers("clients")
        for key in connections:
            dict_connection = json.loads(key)
            redis_session_id = dict_connection['id']
            if session_id == redis_session_id:
                pid = dict_connection['pid']
                try:
                    os.kill(pid, 3)
                    redis_server.srem("clients", key)
                    data = "Session Killed"
                except Exception as e:
                    print e
                    data = str(e)
                break
        return HttpResponse(data)

@permission_required('web.view_session_logs')
def get_sessions(request):
    if request.is_ajax():
        redis_server = redis.Redis(settings.redis_server)
        sessions = map(lambda x: json.loads(x), redis_server.smembers("clients"))
        json_data = json.dumps(sorted(sessions, key=lambda i: i['real_user']))
        return HttpResponse(json_data, content_type="application/json")


# Template Views
class ActiveSessionTemplateView(TemplateView):
    template_name = "web/active_sessions.html"

    @method_decorator(permission_required('web.view_session_logs'))
    def dispatch(self, request, *args, **kwargs):
        return super(ActiveSessionTemplateView, self).dispatch(request, *args, **kwargs)


# Function View
@permission_required('web.view_session_logs')
def download_session_log(request, pk):
    session_log = SessionLog.objects.get(pk=pk)
    log_basename = os.path.basename(session_log.log_file)
    zip_filename = log_basename.replace(".log", ".zip")
    s = StringIO.StringIO()
    zf = zipfile.ZipFile(s, "w")
    zf.write(session_log.log_file, log_basename)
    zf.close()
    resp = HttpResponse(s.getvalue(), mimetype="application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    return resp
