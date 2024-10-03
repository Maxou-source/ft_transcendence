from . import views
from django.conf.urls.static import static
from django.urls import path
from django.urls import re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.conf import settings
from django.views.generic.base import RedirectView
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('home', views.home1, name='home'),
    path('game', views.game, name='game'),
    path('statistics', views.statistics, name='statistics'),
    path('get_tournames/', views.get_tournames, name='get_tournames'),
    path('get_statistics/', views.get_statistics, name='get_statistics'),
    path('params', views.params, name='params'),
    path('friends', views.friends, name='friends'),
    path('home/<str:page>/', views.home, name='home'),
    path('profile/<str:user>/', views.profile, name='profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('upload_avatar/', views.upload_avatar, name='upload_avatar'),
    path('send_friend_request/', views.send_friend_request, name='send_friend_request'),
    path('block_user/', views.block_user , name='block_user'),
    path('remove_friend_request/', views.remove_friend_request, name='remove_friend_request'),
    path('statistics/', views.statistics, name='statistics'),
    path('refresh_access_token/', views.refresh_access_token, name='refresh_token/'),
    #path('favicon.ico/', views.get_favicon, name='get_favicon'),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('images/favicon.ico')))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)