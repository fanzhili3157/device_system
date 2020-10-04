from django import forms

from .models import Device, DeviceType, DeviceHis


# 定义设备表单验证
class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['device_type', 'device_id', 'buy_time', 'device_mac', 'device_root', 'device_status',
                  'description','comment']


# 定义设备类型表单验证
class DeviceTypeForm(forms.ModelForm):
    class Meta:
        model = DeviceType
        fields = ['device_type','device_system','device_cpu','device_res']


# 定义设备表单验证
class DeviceHisForm(forms.ModelForm):
    class Meta:
        model = DeviceHis
        fields = ['device_id', 'device_user', 'device_next_user','expired_date','is_ongoing']