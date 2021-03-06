from django.contrib import admin
from django.urls import path, include

from devices.views import DeviceSumView,DeviceListView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', DeviceListView.as_view(), name='index'),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('devices/', include(('devices.urls', 'devices'), namespace='devices')),
]
