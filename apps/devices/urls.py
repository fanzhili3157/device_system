from django.urls import path

from .views import DeviceListView, DeviceAddView, DeviceDetailView, DeviceModifyView, DeviceDeleteView,DeviceImportView
from .views import TypeListView, TypeAddView, TypeDetailView, TypeModifyView
from .views import DeviceSumView,DeviceMyListView,DeviceSelectNameView,DeviceSelectTimeView
urlpatterns = [
    # 设备url
    path('device/sum/', DeviceSumView.as_view(), name='device_sum'),
    path('device/list/', DeviceListView.as_view(), name='device_list'),
    path('device/add/', DeviceAddView.as_view(), name='device_add'),
    path('device/detail/<device_id>/', DeviceDetailView.as_view(), name='device_detail'),
    path('device/modify/', DeviceModifyView.as_view(), name='device_modify'),
    path('device/delete/<device_id>/', DeviceDeleteView.as_view(), name='device_delete'),
    path('device/import/', DeviceImportView.as_view(), name='device_import'),
    path('device/mylist/', DeviceMyListView.as_view(), name='device_mylist'),
    path('device/selectname/<device_id>/', DeviceSelectNameView.as_view(), name='select_name'),
    path('device/selecttime/<device_id>/', DeviceSelectTimeView.as_view(), name='select_time'),


    # 资产类型url
    path('type/list/', TypeListView.as_view(), name='type_list'),
    path('type/add/', TypeAddView.as_view(), name='type_add'),
    path('type/detail/<int:type_id>/', TypeDetailView.as_view(), name='type_detail'),
    path('type/modify/', TypeModifyView.as_view(), name='type_modify')
]
