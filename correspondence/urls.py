from django.conf.urls import url
from . import views

app_name = 'correspondence'

urlpatterns = [
    url(r'^new_law', views.new_law, name='new_law'),
    url(r'^del_law', views.del_law, name='del_law'),
    url(r'^new_scope', views.new_scope, name='new_scope'),
    url(r'^del_scope', views.del_scope, name='del_scope'),
    url(r'^corr/get_request/(?P<pk>\d+)/$', views.get_request, name='get_request'),
    url(r'^corr/get_correspondence/(?P<counterparty>\d+)$', views.get_correspondence, name='get_correspondence'),
    url(r'^corr/get_correspondence_info', views.get_correspondence_info, name='get_correspondence_info'),
    url(r'^get_request/(?P<pk>\d+)/$', views.get_request, name='get_request'),
    url(r'^add_request', views.add_request, name='add_request'),
    url(r'^edit_request', views.edit_request, name='edit_request'),
    url(r'^deactivate_request/(?P<pk>\d+)$', views.deactivate_request, name='del_request'),
    url(r'^get_correspondence/(?P<counterparty>\d+)$', views.get_correspondence, name='get_correspondence'),
    url(r'^get_correspondence_info', views.get_correspondence_info, name='get_correspondence_info'),
    url(r'^(?P<pk>\d+)/$', views.index, name='index'),
    url(r'corr/', views.index, name='index'),
    url(r'^$', views.index, name='index'),
]
