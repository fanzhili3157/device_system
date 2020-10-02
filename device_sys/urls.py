from django.contrib import admin
from django.urls import path, include

from devices.views import IndexView,ServerListView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('servers/', include(('devices.urls', 'devives'), namespace='devices')),
]
