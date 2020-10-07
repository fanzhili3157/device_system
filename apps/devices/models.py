from users.models import UserProfile
from datetime import datetime
from django.db import models


# 定义设备类型model
class DeviceType(models.Model):
    device_type = models.CharField(max_length=50, verbose_name='设备品牌和型号')
    device_system = models.CharField(max_length=50, verbose_name='设备操作系统')
    device_cpu = models.CharField(max_length=50, verbose_name='cpu')
    device_res = models.CharField(max_length=50, verbose_name='分辨率')
    class Meta:
        verbose_name = '设备品牌和型号'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.device_type

# 定义设备model
class Device(models.Model):
    device_id = models.CharField(max_length=50, verbose_name='资产编号',unique=True)
    device_type = models.ForeignKey(DeviceType,on_delete=models.DO_NOTHING,verbose_name="设备类型")
    buy_time = models.DateField(verbose_name='采购时间')
    device_mac = models.CharField(max_length=50, verbose_name='mac地址', null=True,blank=True)
    device_sys = models.CharField(max_length=50, verbose_name='操作系统', null=True, blank=True)
    device_men = models.CharField(max_length=50, verbose_name='内存', null=True, blank=True)
    device_root = models.CharField(max_length=10, choices=(('1', '是'), ('0', '否')),
                               verbose_name='是否root', default='0')
    device_status = models.CharField(max_length=10, choices=(('1', '占用'), ('0', '空闲'), ('-1', '损坏')),
                                   verbose_name='设备状态', default='0')
    device_user = models.ForeignKey(UserProfile,on_delete=models.DO_NOTHING,verbose_name="使用人",blank=True,null=True)
    expired_date = models.DateField(verbose_name='预计结束时间',  blank=True,null=True)
    #next_user = models.ForeignKey(UserProfile,on_delete=models.DO_NOTHING,verbose_name="下个使用人",blank=True)
    next_user = models.CharField(max_length=50, verbose_name='下个使用人',blank=True)
    description = models.CharField(max_length=100, verbose_name='描述信息', blank=True)
    comment = models.CharField(max_length=300, verbose_name='备注', blank=True)


    class Meta:
        verbose_name = '设备表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.device_id





# 定义设备使用历史model
class DeviceHis(models.Model):
    device_id = models.ForeignKey(Device,on_delete=models.DO_NOTHING,verbose_name='设备id')
    device_user = models.ForeignKey(UserProfile,on_delete=models.DO_NOTHING,verbose_name="使用人")
    start_time = models.DateTimeField(default=datetime.now, verbose_name='开始时间')
    end_time = models.DateTimeField( verbose_name='结束时间',blank=True,null=True)
    is_going = models.CharField(max_length=10, choices=(('1', '进行中'), ('0', '已结束')),
                                verbose_name='进行or结束', default='1', blank=True)

    class Meta:
        verbose_name = '设备使用历史表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.device_id



# 定义设备申请model
class DeviceRequest(models.Model):

    device_id = models.ForeignKey(Device, on_delete=models.DO_NOTHING,verbose_name='资产编号')
    device_req = models.ForeignKey(UserProfile,on_delete=models.DO_NOTHING,verbose_name="申请人",null=True)
    expired_date = models.DateField(verbose_name='预计结束时间')
    duration = models.DurationField
    class Meta:
        verbose_name = '设备使用历史表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.device_req