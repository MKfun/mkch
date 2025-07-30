from django.urls import path, re_path
from . import views


urlpatterns = [
    re_path(r'^board/(?P<pk>\w+)$', views.BoardView.as_view(), name="board_api_view"),
    re_path(r'^board/(?P<bpk>\w+)/thread/(?P<pk>[0-9]+)/comments', views.ThreadView.as_view(), name="thread_api_view"),
]
