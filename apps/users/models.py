from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser

class Department(models.Model):
    department_name = models.CharField(max_length=20, verbose_name='部门名称',unique=True)

    class Meta:
        verbose_name = '部门信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.department_name


# 定义用户模型，添加额外的字段
class UserProfile(AbstractUser):
    department = models.ForeignKey(Department,on_delete=models.DO_NOTHING,null=True)
    seat = models.CharField(max_length=30, verbose_name='工位信息', blank=True)
    mobile = models.CharField(max_length=30, verbose_name='手机号码', blank=True)
    email = models.CharField(max_length=30, verbose_name='邮箱', blank=True)
    isadmin = models.CharField(max_length=10, choices=(('1', '是'), ('0', '否')),
                               verbose_name='是否管理员', default='0', blank=True)
    is_staff = models.CharField(max_length=10, choices=(('1', '是'), ('0', '否')),
                                verbose_name='是否在职', default='1', blank=True)
    modify_time = models.DateTimeField(default=datetime.now, verbose_name='修改时间')

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username




