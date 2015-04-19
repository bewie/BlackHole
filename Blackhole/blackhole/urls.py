from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'blackhole.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'web/login.html'}),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/web/'}),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^web/', include('web.urls')),
)
