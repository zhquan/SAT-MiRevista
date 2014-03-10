from django.conf.urls import patterns, include, url
from django.conf.urls.defaults import *
from django.contrib.auth.views import login
from django.contrib.auth.views import logout
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #admin, register, login, logout, template
    url(r'^admin/', include(admin.site.urls)),
    url(r'^register$', 'revista.views.register'),
    url(r'^templates/(?P<path>.*)$', 'django.views.static.serve',{'document_root': 'templates'}),
    url(r'^login$', 'django.contrib.auth.views.login'),
    url(r'^accounts/profile/$', 'revista.views.profile'),
    url(r'^logout$', 'django.contrib.auth.views.logout',{'next_page': '/'}),
    url(r'^titulo$', 'revista.views.titulo'),
    #Home
    url(r'^$', 'revista.views.home'), 
    #Canales
    url(r'^canales$', 'revista.views.canales'),
    url(r'^canales/guardar/(.*)/(.*)/(.*)$', 'revista.views.guardar'),
    url(r'^canales/(\d+)$', 'revista.views.CanalNum'),
    #Ayuda
    url(r'^ayuda$', 'revista.views.ayuda'),
    #Usuario
    url(r'^(.*)/rss$', 'revista.views.RSS'),
    url(r'^(.*)$', 'revista.views.usuario'),
    
)
