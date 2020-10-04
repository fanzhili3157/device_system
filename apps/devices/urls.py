from django.urls import path

from .views import DeviceListView, DeviceAddView, DeviceDetailView, DeviceModifyView, DeviceDeleteView
from .views import TypeListView, TypeAddView, TypeDetailView, TypeModifyView

urlpatterns = [
    # 设备url
    path('device/list/', DeviceListView.as_view(), name='device_list'),
    path('device/add/', DeviceAddView.as_view(), name='device_add'),
    path('device/detail/<device_id>/', DeviceDetailView.as_view(), name='device_detail'),
    path('device/modify/', DeviceModifyView.as_view(), name='device_modify'),
    path('device/delete/<device_id>/', DeviceDeleteView.as_view(), name='device_delete'),
    #path('device/export/', ServerExportView.as_view(), name='server_export'),

    # 资产类型url
    path('type/list/', TypeListView.as_view(), name='type_list'),
    path('type/add/', TypeAddView.as_view(), name='type_add'),
    path('type/detail/<int:type_id>/', TypeDetailView.as_view(), name='type_detail'),
    path('type/modify/', TypeModifyView.as_view(), name='type_modify')
]
