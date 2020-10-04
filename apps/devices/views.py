from django.shortcuts import render
from django.views.generic.base import View
from django.http.response import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db.models import Q, Count
from pure_pagination import Paginator, PageNotAnInteger
import csv

from .models import Device, DeviceType, DeviceHis
from .forms import DeviceForm, DeviceTypeForm,DeviceHisForm
from users.models import UserOperateLog, UserProfile
from device_sys.settings import per_page
from utils.mixin_utils import LoginRequiredMixin


# 定义首页视图
class IndexView(View):
    def get(self, request):
        search = request.GET.get('search')
        if search:
            search = request.GET.get('search').strip()
            # 如果输入的是纯数字，则将序号也加入到搜索的列表中来
            try:
                search_int = int(search)
                devices = Device.objects.filter(Q(id=search_int) | Q(device_type__device_type__icontains=search)
                                                | Q(device_brand__icontains=search) | Q(device_id__icontains=search)
                                                | Q(device_user__icontains=search) | Q(device_status__icontains=search)
                                                | Q(device_type__system__icontains=search) | Q(device_type__cpu__icontains=search)
                                                | Q(device_type__men__icontains=search) | Q(device_type__res__icontains=search)). \
                    order_by('device_type', 'id')
            except Exception:
                devices = Device.objects.filter(Q(device_type__device_type__icontains=search)
                                                | Q(device_brand__icontains=search) | Q(device_id__icontains=search)
                                                | Q(device_user__icontains=search) | Q(device_status__icontains=search)
                                                | Q(device_type__system__icontains=search) | Q(device_type__cpu__icontains=search)
                                                | Q(device_type__men__icontains=search) | Q(device_type__res__icontains=search)). \
                    order_by('device_type', 'id')
        else:
            devices = Device.objects.all().order_by('device_type', 'id')

        # 分页功能实现
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(devices, per_page=per_page, request=request)
        p_devices = p.page(page)
        start = (int(page)-1) * per_page  # 避免分页后每行数据序号从1开始
        return render(request, 'devices/device_list.html', {'p_devices': p_devices, 'start': start, 'search': search})

# 设备列表
class DeviceListView(View):
    def get(self, request):
        search = request.GET.get('search')
        if search:
            search = request.GET.get('search').strip()
            # 如果输入的是纯数字，则将序号也加入到搜索的列表中来
            try:
                search_int = int(search)
                devices = Device.objects.filter(Q(id=search_int) | Q(device_type__device_type__icontains=search)
                                                | Q(device_brand__icontains=search) | Q(device_id__icontains=search)
                                                | Q(device_user__icontains=search) | Q(device_status__icontains=search)
                                                | Q(device_type__system__icontains=search) | Q(device_type__cpu__icontains=search)
                                                | Q(device_type__men__icontains=search) | Q(device_type__res__icontains=search)). \
                    order_by('device_type', 'id')
            except Exception:
                devices = Device.objects.filter(Q(device_type__device_type__icontains=search)
                                                | Q(device_brand__icontains=search) | Q(device_id__icontains=search)
                                                | Q(device_user__icontains=search) | Q(device_status__icontains=search)
                                                | Q(device_type__system__icontains=search) | Q(device_type__cpu__icontains=search)
                                                | Q(device_type__men__icontains=search) | Q(device_type__res__icontains=search)). \
                    order_by('device_type', 'id')
        else:
            devices = Device.objects.all().order_by('device_type', 'id')

            uses = DeviceHis.objects.filter(is_ongoing='1')

            for u in uses:
                print(u.device_id)

        # 分页功能实现
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(devices, per_page=per_page, request=request)
        p_devices = p.page(page)
        print(p_devices)
        start = (int(page)-1) * per_page  # 避免分页后每行数据序号从1开始
        return render(request, 'devices/device_list.html', {'p_devices': p_devices, 'uses':uses,'start': start, 'search': search})


# 设备添加
class DeviceAddView(LoginRequiredMixin, View):
    def get(self, request):
        users = UserProfile.objects.filter(is_superuser=0, is_staff='1')
        device_types = DeviceType.objects.all()
        return render(request, 'devices/device_add.html', {'users': users, 'devices_types': device_types})

    def post(self, request):
        device_form = DeviceForm(request.POST)
        # 判断表单是否正确
        if device_form.is_valid():  #更新设备表
            device_type = request.POST.get('device_type').strip()
            device_id = request.POST.get('device_id').strip()
            buy_time = request.POST.get('buy_time').strip()
            device_mac = request.POST.get('device_mac').strip()
            device_root = request.POST.get('device_root')
            device_status = request.POST.get('device_status').strip()
            device_user = request.POST.get('device_user').strip()
            expired_date = request.POST.get('expired_date').strip()
            comment = request.POST.get('comment').strip()

            dev_id = Device.objects.filter(device_id=device_id)
            if dev_id:
                return render(request,'devices/device_add.html',{'msg':'资产编号重复'})

            if device_status=='1': #如果是使用中，检查使用人信息和时间
                if device_form.data['device_user'] !='' and device_form.data['expired_date'] !='':

                    device_user = request.POST.get('device_user').strip()
                    expired_date = request.POST.get('expired_date').strip()
                    if UserProfile.objects.filter(username=device_user):
                        new_use = DeviceHis(device_id=device_id,device_user=device_user,expired_date=expired_date)
                        new_use.save()
                        new_device = Device(device_type=device_type, device_id=device_id, buy_time=buy_time,
                                            device_mac=device_mac, device_root=device_root,
                                            device_status=device_status, device_user=device_user,
                                            expired_date=expired_date, comment=comment)
                        new_device.save()
                    else:
                        return render(request, 'devices/device_add.html', {'msg': '用户不存在'})
                else:
                    device_types = DeviceType.objects.all()
                    return render(request, 'devices/device_add.html', {'msg': '输入使用人和日期','device_form':device_form,'device_types':device_types})
            else: #如果是空闲，则忽略使用人和时间
                new_device = Device(device_type=device_type, device_id=device_id, buy_time=buy_time,
                                    device_mac=device_mac, device_root=device_root,
                                    device_status=device_status,
                                    comment=comment)
                new_device.save()


            return HttpResponseRedirect((reverse('devices:device_list')))

            # device_user = UserProfile.objects.filter(username=request.POST.get('device_user', 0)).first()

            #
            # user_name = device_user.username if device_user else ''
            #
            # # 该记录添加到历史表中
            # device_his = DeviceHis(deviceid=new_device.id, device_type=device_type.device_type, device_id=device_id,
            #                        device_mac=device_mac, device_root=device_root, device_status=device_status, device_user=device_user,
            #                        comment=comment)
            # device_his.save()
            #
            # # 将操作记录添加到日志中
            # new_log = UserOperateLog(username=request.user.username, scope=device_type.device_type, type='增加',
            #                          content=device_his.deviceid)
            # new_log.save()
            # return HttpResponseRedirect((reverse('devices:device_list')))
        else:
            device_types = DeviceType.objects.all()
            return render(request, 'devices/device_add.html', {'msg': '输入错误！', 'device_form': device_form, 'device_types': device_types})


# 设备详情
class DeviceDetailView(LoginRequiredMixin, View):
    def get(self, request, device_id):
        device = Device.objects.filter(device_id=device_id).first()
        users = UserProfile.objects.filter(is_superuser=0, is_staff='1')
        device_types = DeviceType.objects.all()
        device_his = DeviceHis.objects.filter(device_id=device_id)

        # 分页功能实现
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(device_his, per_page=per_page, request=request)
        p_device_his = p.page(page)
        start = (int(page)-1) * per_page  # 避免分页后每行数据序号从1开始
        return render(request, 'devices/device_detail.html', {'users': users, 'device': device,
                                                              'device_types': device_types,
                                                              'p_device_his': p_device_his, 'start': start})


# 设备修改
class DeviceModifyView(LoginRequiredMixin, View):
    def post(self, request):
        device_id = int(request.POST.get('device_id'))
        device = Device.objects.filter(id=device_id).first()
        device_form = DeviceForm(request.POST)
        # 判断表单是否正确
        if device_form.is_valid():

            #空闲->使用
            #使用 ->空闲
            #使用 -> 使用

            #device.device_type = DeviceType.objects.filter(id=request.POST.get('device_type')).first()
            #device.device_id = request.POST.get('device_id').strip()
            device.device_mac = request.POST.get('device_mac').strip()
            device.device_root = request.POST.get('device_root').strip()
            device.device_status = request.POST.get('device_status').strip()
            device.device_user = request.POST.get('device_user')
            device.expired_date = request.POST.get('expired_date').strip()
            device.comment = request.POST.get('comment').strip()

            device.save()

            user_name = device.device_user.username if device.device_user else ''

            # 该记录添加到历史表中
            device_his = DeviceHis(deviceid=device.id, device_type=device.device_type.device_type, device_id=device.device_id,
                                   device_mac=device.device_mac, device_root=device.device_root, device_status=device.device_status, device_user=device.device_user,
                                   comment=device.comment)
            device_his.save()

            # 将操作记录添加到日志中
            new_log = UserOperateLog(username=request.user.username, scope=device.device_type, type='修改',
                                     content=device_id)
            new_log.save()
            return HttpResponseRedirect((reverse('devices:device_list')))
        else:
            users = UserProfile.objects.filter(is_superuser=0, is_staff='1')
            device_types = DeviceType.objects.all()
            return render(request, 'devices/device_detail.html', {'users': users, 'device': device,
                                                                  'device_types': device_types,
                                                                  'msg': '输入错误！', 'device_form': device_form})


# 设备删除
class DeviceDeleteView(LoginRequiredMixin, View):
    def get(self, request, device_id):
        device = Device.objects.get(id=device_id)
        scope = device.device_type
        user_name = device.device_user.username if device.device_user else ''

        # 该记录添加到历史表中
        device_his = DeviceHis(device_id=device.id, device_type=device.device_type.device_type,
                                   device_mac=device.device_mac, device_root=device.device_root,
                               device_status=device.device_status, device_user=device.device_user,
                               comment='该记录被删除')
        device_his.save()

        # 删除该记录
        device.delete()

        # 将操作记录添加到日志中
        new_log = UserOperateLog(username=request.user.username, scope=device.device_type, type='删除',
                                 content=str(device_id))
        new_log.save()
        return HttpResponseRedirect((reverse('devices:device_list')))


# # 资产列表导出
# class deviceExportView(LoginRequiredMixin, View):
#     def get(self, request):
#         search = request.GET.get('search')
#         if search:
#             search = request.GET.get('search').strip()
#             devices = Device.objects.filter(Q(zctype__zctype__icontains=search) | Q(ipaddress__icontains=search)
#                                             | Q(description__icontains=search) | Q(brand__icontains=search)
#                                             | Q(zcmodel__icontains=search) | Q(zcnumber__icontains=search)
#                                             | Q(zcpz__icontains=search) | Q(owner__username__icontains=search)).\
#                 order_by('zctype')
#         else:
#             devices = Device.objects.all().order_by('zctype')
#         devices = devices.values('id', 'zctype__zctype', 'ipaddress', 'description', 'brand', 'zcmodel', 'zcnumber',
#                                  'zcpz', 'owner__username', 'undernet', 'guartime', 'comment')
#         colnames = ['序号', '资产类型', 'IP地址', '功能描述', '设备品牌', '设备型号', '设备序号', '设备配置',
#                     '管理人员', '所在网络', '保修期', '备注']
#         response = create_excel(colnames, devices, 'zcgl')
#         return response
#
#
# def create_excel(columns, content, file_name):
#     """创建导出csv的函数"""
#     file_name = file_name + '.csv'
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename=' + file_name
#     response.charset = 'gbk'
#     writer = csv.writer(response)
#     writer.writerow(columns)
#     for i in content:
#         writer.writerow([i['id'], i['zctype__zctype'], i['ipaddress'], i['description'], i['brand'], i['zcmodel'],
#                          i['zcnumber'], i['zcpz'], i['owner__username'], i['undernet'], i['guartime'], i['comment']])
#     return response


# 设备类型列表
class TypeListView(LoginRequiredMixin, View):
    # def get(self, request):
    #     device_types = DeviceType.objects.all()
    #     print(device_types)
    #     return render(request, 'devices/type_list.html', {'device_types': device_types})
    def get(self, request):
        search = request.GET.get('search')
        if search:
            search = request.GET.get('search').strip()
            device_types = DeviceType.objects.filter(Q(device_type__icontains=search))
        else:
            device_types = DeviceType.objects.all()

        # 分页功能实现
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(device_types, per_page=per_page, request=request)
        p_device_types = p.page(page)
        start = (int(page) - 1) * per_page  # 避免分页后每行数据序号从1开始

        return render(request, 'devices/type_list.html', {'p_device_types': p_device_types, 'start': start, 'search': search})

# 设备类型添加
class TypeAddView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'devices/type_add.html', {})

    def post(self, request):
        device_type = request.POST.get('device_type').strip()
        device_system = request.POST.get('device_system').strip()
        device_cpu = request.POST.get('device_cpu').strip()
        device_res = request.POST.get('device_res').strip()
        devicetype_form = DeviceTypeForm(request.POST)
        # 判断表单是否正确
        if devicetype_form.is_valid():
            other_devicetype = DeviceType.objects.filter(device_type=device_type)
            # 判断是否已经存在了该类型
            if other_devicetype:
                return render(request, 'devices/type_add.html', {'msg': device_type+' 已存在！'})
            else:
                new_devicetype = DeviceType(device_type=device_type,device_system=device_system,device_cpu=device_cpu,
                                            device_res=device_res)
                new_devicetype.save()
                return HttpResponseRedirect((reverse('devices:type_list')))
        else:
            return render(request, 'devices/type_add.html', {'msg': '输入错误！', 'devicetype_form': devicetype_form})


# 设备类型详情
class TypeDetailView(LoginRequiredMixin, View):
    def get(self, request, type_id):
        device_type = DeviceType.objects.get(id=type_id)
        return render(request, 'device/type_detail.html', {'device_type': device_type})


# 设备类型修改
class TypeModifyView(LoginRequiredMixin, View):
    def post(self, request):
        type_id = int(request.POST.get('type_id'))
        device_type = request.POST.get('device_type').strip()
        exist_device_type = DeviceType.objects.get(id=type_id)
        other_device_type = DeviceType.objects.filter(~Q(id=type_id), device_type=device_type)
        devicetype_form = DeviceTypeForm(request.POST)
        # 判断表单是否正确
        if devicetype_form.is_valid():
            # 如果修改了资产类型名字，判断是否该名字与其他资产类型名字冲突
            if other_device_type:
                return render(request, 'devices/type_detail.html', {'device_type': exist_device_type,
                                                                    'msg': device_type+' 已存在！'})
            else:
                exist_device_type.device_type = device_type
                exist_device_type.save()
                return HttpResponseRedirect((reverse('devices:type_list')))
        else:
            return render(request, 'devices/type_detail.html', {'device_type': exist_device_type,
                                                                'msg': '输入错误！',
                                                                'devicetype_form': devicetype_form})
