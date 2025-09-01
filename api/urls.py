from django.urls import path, re_path
from . import views


urlpatterns = [
    path('boards/', views.BoardListView.as_view(), name="board_list_api_view"),
    re_path(r'^board/(?P<pk>\w+)$', views.BoardView.as_view(), name="board_api_view"),
    re_path(r'^board/(?P<pk>\w+)/thread/(?P<tpk>[0-9]+)/comments', views.ThreadView.as_view(), name="thread_api_view"),
    re_path(r'^board/(?P<pk>\w+)/thread/(?P<tpk>[0-9]+)$', views.ThreadDetailView.as_view(), name="thread_detail_api_view")
]
