from django.urls import path

from .views import ServerListView, ServerAddView, ServerDetailView, ServerModifyView, ServerDeleteView, ServerExportView
from .views import TypeListView, TypeAddView, TypeDetailView, TypeModifyView

urlpatterns = [
    # 设备url
    path('device/list/', ServerListView.as_view(), name='server_list'),
    path('device/add/', ServerAddView.as_view(), name='server_add'),
    path('device/detail/<int:device_id>/', ServerDetailView.as_view(), name='server_detail'),
    path('device/modify/', ServerModifyView.as_view(), name='server_modify'),
    path('device/delete/<int:server_id>/', ServerDeleteView.as_view(), name='server_delete'),
    path('device/export/', ServerExportView.as_view(), name='server_export'),

    # 资产类型url
    path('type/list/', TypeListView.as_view(), name='type_list'),
    path('type/add/', TypeAddView.as_view(), name='type_add'),
    path('type/detail/<int:type_id>/', TypeDetailView.as_view(), name='type_detail'),
    path('type/modify/', TypeModifyView.as_view(), name='type_modify')
]
