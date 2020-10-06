from django import forms
from django.core.exceptions import ValidationError

from .models import Device, DeviceType, DeviceHis,DeviceRequest

# 定义设备类型表单验证
class DeviceTypeForm(forms.ModelForm):
    class Meta:
        model = DeviceType
        fields = ['device_type','device_system','device_cpu','device_res']

# 定义设备表单验证
class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['device_type', 'device_id', 'buy_time', 'device_mac', 'device_men','device_root', 'device_status','device_sys',
                  'device_user','next_user','expired_date','description','comment']

class DeviceModifyForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['device_type', 'device_id', 'device_mac', 'device_men','device_root', 'device_status','device_sys',
                  'device_user','next_user','expired_date','description','comment']
# 定义设备表单验证
class DeviceHisForm(forms.ModelForm):
    class Meta:
        model = DeviceHis
        fields = ['device_id', 'device_user', 'start_time','end_time']

class DeviceReq(forms.ModelForm):
    class Meta:
        model = DeviceRequest
        fields = ['device_id','device_req']

class UploadExcelForm(forms.Form):
    excel = forms.FileField(validators=[])

def validate_excel(value):
    if value.name.split('.')[-1] not in ['xls','xlsx']:
        raise ValidationError('Invalid File Type')