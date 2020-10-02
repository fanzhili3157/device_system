from django.contrib import admin

from .models import Device, DeviceType


class DeviceAdmin(admin.ModelAdmin):
    pass


class DeviceTypeAdmin(admin.ModelAdmin):
    pass

admin.site.register(Device, DeviceAdmin)
admin.site.register(DeviceType, DeviceTypeAdmin)
