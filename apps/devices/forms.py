from django import forms

from .models import Device, DeviceType


# 定义设备表单验证
class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['device_type', 'device_brand', 'device_id', 'device_user', 'buy_time', 'device_mac', 'device_root', 'device_status',
                  'comment']


# 定义设备类型表单验证
class DeviceTypeForm(forms.ModelForm):
    class Meta:
        model = DeviceType
        fields = ['device_type','device_system','device_cpu','device_men']

