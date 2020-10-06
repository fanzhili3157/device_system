from django.contrib import admin

from .models import Device, DeviceType


class DeviceAdmin(admin.ModelAdmin):
    search_fileds = ['device_id','device_user','device_type__device_type']


class DeviceTypeAdmin(admin.ModelAdmin):
    pass

admin.site.register(Device, DeviceAdmin)
admin.site.register(DeviceType, DeviceTypeAdmin)
