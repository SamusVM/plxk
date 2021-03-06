from django.conf.urls import url
from . import views, views_org_structure, views_counterparties, views_non_compliances
from docs.views_contracts import get_info_for_contracts_page, get_contracts, get_contract, \
    get_simple_contracts_list, add_contract
from correspondence.views import get_correspondence, get_correspondence_info, get_request
from edms.views import edms_get_table_first, edms_get_table_all, edms_get_doc, edms_mark


app_name = 'boards'

urlpatterns = [
    url(r'^$', views.forum, name='index'),
    url(r'^(?P<pk>\d+)/$', views.board_topics, name='topics'),
    url(r'^(?P<pk>\d+)/new/$', views.new_topics, name='new_topic'),

    url(r'^plhk_ads/', views.plhk_ads, name='plhk_ads'),
    url(r'^plhk_ads/reload/', views.reload, name='reload'),
    url(r'^edit_ads/', views.edit_ads, name='edit_ads'),
    url(r'^new_ad/', views.new_ad, name='new_ad'),
    url(r'^del_ad/(?P<pk>\d+)/$', views.del_ad, name='del_ad'),

    url(r'^.+/add_contract', add_contract, name='add_contract'),
    url(r'^.+/get_non_compliances/(?P<counterparty>\w+)/(?P<page>\d+)/$', views_non_compliances.get_non_compliances, name='get_non_compliances'),
    url(r'^.+/get_non_compliance/(?P<pk>\d+)/$', views_non_compliances.get_non_compliance, name='get_non_compliance'),
    url(r'^.+/post_non_compliance', views_non_compliances.post_non_compliance, name='post_non_compliance'),
    url(r'^.+/dep_chief_approval', views_non_compliances.dep_chief_approval, name='dep_chief_approval'),
    url(r'^.+/post_new_comment', views_non_compliances.post_new_comment, name='post_new_comment'),
    url(r'^.+/post_decision', views_non_compliances.post_decision, name='post_decision'),
    url(r'^.+/non_compliance_done', views_non_compliances.done, name='done'),

    url(r'^org_structure/get_seat_info/(?P<pk>\d+)/$', views_org_structure.get_seat_info, name='get_seat_info'),
    url(r'^org_structure/post_instruction/', views_org_structure.post_instruction, name='post_instruction'),
    url(r'^org_structure/', views_org_structure.org_structure, name='org_structure'),

    url(r'^providers/get_providers/(?P<wood_only>\w+)/(?P<page>\d+)/$', views_counterparties.get_providers, name='get_providers'),
    url(r'^providers/get_provider/(?P<pk>\d+)/$', views_counterparties.get_provider, name='get_provider'),
    url(r'^providers/post_provider/', views_counterparties.post_provider, name='post_provider'),
    url(r'^providers/deact_counterparty/(?P<pk>\d+)/$', views_counterparties.deact_counterparty, name='deact_counterparty'),
    url(r'^providers/get_certification/(?P<provider_id>\d+)/$', views_counterparties.get_certification, name='get_certification'),
    url(r'^providers/post_certificate/', views_counterparties.post_certificate, name='post_certificate'),
    url(r'^providers/deact_certificate/(?P<pk>\d+)/$', views_counterparties.deact_certificate, name='deact_certificate'),
    url(r'^providers/get_certificate/(?P<pk>\d+)/$', views_counterparties.get_certificate, name='get_certificate'),
    url(r'^providers/post_certificate_pause/', views_counterparties.post_certificate_pause, name='post_certificate_pause'),
    url(r'^providers/deact_cert_pause/(?P<pk>\d+)/$', views_counterparties.deact_cert_pause, name='deact_cert_pause'),
    url(r'^providers/get_info_for_contracts_page', get_info_for_contracts_page, name='get_info_for_contracts_page'),
    url(r'^providers/get_contracts/(?P<counterparty>-?\d+)/(?P<company>\w+)/(?P<with_add>\w+)/(?P<page>\w+)/$', get_contracts, name='get_contracts'),
    url(r'^providers/get_contract/(?P<pk>\d+)/$', get_contract, name='get_contract'),
    url(r'^providers/get_simple_contracts_list/(?P<counterparty>\w+)/(?P<company>\w+)/$', get_simple_contracts_list, name='get_simple_contracts_list'),
    url(r'^providers/get_counterparties_for_select/', views_counterparties.get_counterparties_for_select, name='get_counterparties_for_select'),
    url(r'^providers/', views_counterparties.providers, name='providers'),

    url(r'^clients/get_clients/(?P<page>\d+)/$', views_counterparties.get_clients, name='get_clients'),
    url(r'^clients/get_client/(?P<pk>\d+)/$', views_counterparties.get_client, name='get_client'),
    url(r'^clients/post_client/', views_counterparties.post_client, name='post_client'),
    url(r'^clients/deact_counterparty/(?P<pk>\d+)/$', views_counterparties.deact_counterparty, name='deact_counterparty'),
    url(r'^clients/get_info_for_contracts_page', get_info_for_contracts_page, name='get_info_for_contracts_page'),
    url(r'^clients/get_contracts/(?P<counterparty>-?\d+)/(?P<company>\w+)/(?P<with_add>\w+)/(?P<page>\w+)/$', get_contracts, name='get_contracts'),
    url(r'^clients/get_contract/(?P<pk>\d+)/$', get_contract, name='get_contract'),
    url(r'^clients/get_simple_contracts_list/(?P<counterparty>\w+)/(?P<company>\w+)/$', get_simple_contracts_list, name='get_simple_contracts_list'),
    url(r'^clients/get_counterparties_for_select/', views_counterparties.get_counterparties_for_select, name='get_counterparties_for_select'),
    url(r'^clients/get_correspondence/(?P<counterparty>\d+)$', get_correspondence, name='get_correspondence'),
    url(r'^clients/get_correspondence_info', get_correspondence_info, name='get_correspondence_info'),
    url(r'^clients/get_request/(?P<pk>\d+)/$', get_request, name='get_request'),
    url(r'^clients/get_table_first/(?P<doc_type>\d+)/(?P<counterparty>\d+)/$', edms_get_table_first, name='get_table_first'),
    url(r'^clients/get_table_all/(?P<doc_type>\d+)/(?P<counterparty>\d+)/$', edms_get_table_all, name='get_table_all'),
    url(r'^clients/get_doc/(?P<pk>\d+)/$', edms_get_doc, name='get_doc_info'),
    url(r'^clients/mark/', edms_mark, name='my_docs_mark'),
    url(r'^clients/', views_counterparties.clients, name='clients'),

    url(r'^non_compliances/', views_non_compliances.non_compliances, name='non_compliances'),
]
