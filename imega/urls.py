
from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import url
from django.views.static import serve
from photo.views import me, index, join, AlbumView, avatar, account, like
from .settings import MEDIA_ROOT

urlpatterns = [
    path('', index),
    path('in/', join),
    path("me/avatar", avatar),
    path('me/', me),
    path('like/', like),
    url("^account/(.*)", account),
    url('^album$', AlbumView.as_view()),
    url('album/(.*)', AlbumView.as_view()),
    url('^download/(.*)$', AlbumView.download),
    path('admin/', admin.site.urls),
    re_path('^image/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),
]
