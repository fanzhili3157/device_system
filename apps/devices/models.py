from users.models import UserProfile
from datetime import datetime
from django.db import models




# 定义资产model
class Device(models.Model):
    device_type = models.ForeignKey('devices.DeviceType', on_delete=models.CASCADE)
    device_brand = models.CharField(max_length=50, verbose_name='设备品牌', blank=True)
    device_id = models.CharField(max_length=100, verbose_name='资产编号', blank=True)
    device_user = models.ForeignKey('users.UserProfile', on_delete=models.SET_NULL, null=True, blank=True)
    buy_time = models.DateTimeField(default=datetime.now, verbose_name='采购时间')
    device_mac = models.CharField(max_length=50, verbose_name='mac地址', blank=True)
    device_root = models.CharField(max_length=10, choices=(('1', '是'), ('0', '否')),
                               verbose_name='是否root', default='0', blank=True)
    device_status = models.CharField(max_length=10, choices=(('1', '占用'), ('0', '空闲'), ('-1', '损坏')),
                                   verbose_name='设备状态', default='0', blank=True)
    description = models.CharField(max_length=50, verbose_name='描述信息', blank=True)
    comment = models.CharField(max_length=300, verbose_name='备注', blank=True)


    class Meta:
        verbose_name = '设备表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.device_type


# 定义设备类型model
class DeviceType(models.Model):
    device_type = models.CharField(max_length=20, verbose_name='设备品牌和型号')
    device_system = models.CharField(max_length=20, verbose_name='设备操作系统')
    device_cpu = models.CharField(max_length=20, verbose_name='cpu')
    device_men = models.CharField(max_length=20, verbose_name='内存')
    device_res = models.CharField(max_length=20, verbose_name='分辨率')

    class Meta:
        verbose_name = '设备品牌和型号'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.device_type


# 定义设备使用历史model
class DeviceHis(models.Model):
    device_id = models.IntegerField(verbose_name='ID')
    device_his = models.ForeignKey('devices.Device')
    modify_time = models.DateTimeField(default=datetime.now, verbose_name='修改时间')

    class Meta:
        verbose_name = '资产历史表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.device_his
