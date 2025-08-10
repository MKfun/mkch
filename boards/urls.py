from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('lockdown', views.lockdown_all, name='lockdown'),    # ТОЛЬКО POST ЗАПРОСЫ
    path('pin',  views.pin_toggle, name="pin_thread_view"),   # ТОЛЬКО POST ЗАПРОСЫ
    re_path(r'^board/(?P<pk>\w+)$', views.ThreadListView.as_view(), name="board"),
    re_path(r'^board/(?P<pk>\w+)/new$', views.create_new_thread, name="create_thread"),
    re_path(r'^board/(?P<pk>\w+)/thread/(?P<tpk>[0-9]+)/comment$', views.add_comment_to_thread , name="add_comment_to_thread"),
    re_path(r'^board/(?P<bpk>\w+)/thread/(?P<pk>[0-9]+)$', views.ThreadDetailView.as_view(), name="thread_detail_view"),
]

handler404 = views.handler404
