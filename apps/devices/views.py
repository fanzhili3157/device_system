from django.shortcuts import render
from django.views.generic.base import View
from django.http.response import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db.models import Q, Count
from pure_pagination import Paginator, PageNotAnInteger
from datetime import date
from django.contrib.auth.hashers import make_password
import xlrd
import datetime

from .models import Device, DeviceType, DeviceHis
from .forms import DeviceForm, DeviceTypeForm,DeviceModifyForm,UploadExcelForm
from users.models import UserProfile,Department
from device_sys.settings import per_page
from utils.mixin_utils import LoginRequiredMixin

pwd='123456'

# 定义统计视图
class DeviceSumView(View):
    def get(self, request):

        device_counts = DeviceHis.objects.values("device_id__device_type").annotate(counts=Count(id)).order_by('-counts')[:20]
        device_list = []
        device_count = []
        for item in device_counts:
            dev_id = item['device_id__device_type']
            dev_count = item['counts']
            dev_name = DeviceType.objects.filter(id=dev_id).first()


            device_list.append(dev_name)
            device_count.append(dev_count)
        device_types = Device.objects.values("device_type").annotate(counts=Count(id)).order_by('-counts')[:20]
        types_num = DeviceType.objects.all()
        dict_dev = []
        total = len(types_num)
        other = total
        for t in device_types:
            dev_type = DeviceType.objects.filter(id=t['device_type']).first()
            dev_type_name = dev_type.device_type
            dict_dev.append([dev_type_name,t['counts']/total])
            total -= t['counts']
        dict_dev.append(['other',other/total])

        print(dict_dev)

        return render(request, 'devices/device_sum.html', {'device_list':device_list,
                                                           'device_count':device_count,
                                                           'dict_dev':dict_dev})

# 设备列表
class DeviceListView(View):
    def get(self, request):
        search = request.GET.get('search')
        if search:
            dict_status = {'空闲':'0','占用':'1','损坏':'-1'}
            search = request.GET.get('search').strip()
            if search in dict_status.keys():
                search = dict_status[search]
                devices = Device.objects.filter(device_status__icontains=search)
            else:

                devices = Device.objects.filter(Q(device_id__icontains=search)|Q(device_type__device_type__icontains=search)
                                            |Q(device_user__username__icontains=search)|Q(device_sys__icontains=search)
                                            |Q(device_men__icontains=search)|Q(device_type__device_system__icontains=search)
                                            |Q(device_type__device_res__icontains=search))

        else:
            devices = Device.objects.all()

            #uses = DeviceHis.objects.filter(is_ongoing='1')


        # 分页功能实现
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(devices, per_page=per_page, request=request)
        p_devices = p.page(page)
        print(p_devices)
        start = (int(page)-1) * per_page  # 避免分页后每行数据序号从1开始
        return render(request, 'devices/device_list.html', {'p_devices': p_devices,'start': start, 'search': search,'num':len(devices)})



# 设备添加
class DeviceAddView(LoginRequiredMixin, View):
    def get(self, request):
        users = UserProfile.objects.filter(is_staff='1')
        device_types = DeviceType.objects.all()
        return render(request, 'devices/device_add.html', {'users': users, 'devices_types': device_types})

    def post(self, request):
        device_form = DeviceForm(request.POST)
        print(device_form)
        # 判断表单是否正确
        if device_form.is_valid():  #更新设备表
            device_id = request.POST.get('device_id').strip()
            #device_type = request.POST.get('device_type').strip()
            device_type = DeviceType.objects.filter(id=request.POST.get('device_type',0)).first()
            buy_time = request.POST.get('buy_time').strip()
            device_mac = request.POST.get('device_mac').strip()
            device_sys = request.POST.get('device_sys').strip()
            device_men = request.POST.get('device_men').strip()
            device_root = request.POST.get('device_root')
            device_status = request.POST.get('device_status').strip()
            #device_user = request.POST.get('device_user').strip()


            comment = request.POST.get('comment').strip()

            dev_id = Device.objects.filter(device_id=device_id)
            admin_user = UserProfile.objects.filter(isadmin='1').first()
            if dev_id:
                return render(request,'devices/device_add.html',{'msg':'资产编号重复'})

            if device_status=='1': #如果是使用中，检查使用人信息和时间
                if request.POST.get('device_user')  and request.POST.get('expired_date') :

                    #device_user = request.POST.get('device_user').strip()
                    device_user = UserProfile.objects.filter(id=request.POST.get('device_user', 0)).first()
                    expired_date = request.POST.get('expired_date').strip()
                    if device_user:
                        # new_use = DeviceHis(device_id=device_id,device_user=device_user)
                        # new_use.save()
                        new_device = Device(device_type=device_type, device_id=device_id, buy_time=buy_time,
                                            device_mac=device_mac, device_root=device_root,
                                            device_sys=device_sys,device_men=device_men,
                                            device_status=device_status, device_user=device_user,
                                            expired_date=expired_date, comment=comment)
                        new_device.save()

                        deviceLog(new_device, '0', device_status, 0, new_device.device_user)

                    else:
                        return render(request, 'devices/device_add.html', {'msg': '用户不存在'})
                else:
                    device_types = DeviceType.objects.all()
                    return render(request, 'devices/device_add.html', {'msg': '输入使用人和日期','device_form':device_form,'device_types':device_types})
            else: #如果是空闲，则忽略使用人和时间
                new_device = Device(device_type=device_type, device_id=device_id, buy_time=buy_time,
                                    device_mac=device_mac, device_root=device_root,
                                    device_status=device_status,device_user=admin_user,
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
        device = Device.objects.filter(id=device_id).first()
        users = UserProfile.objects.filter(is_superuser=0, is_staff='1')
        device_types = DeviceType.objects.all()
        device_his = DeviceHis.objects.filter(device_id_id=device_id)
        #分页功能实现
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
        device_form = DeviceModifyForm(request.POST)
        status_pre = device.device_status
        user_pre = device.device_user
        # 判断表单是否正确


        if device_form.is_valid():
            device.device_mac = request.POST.get('device_mac').strip()
            device.device_root = request.POST.get('device_root').strip()
            device.device_status = request.POST.get('device_status').strip()
            device.device_sys = request.POST.get('device_sys').strip()
            device.device_men = request.POST.get('device_men').strip()
            device.comment = request.POST.get('comment').strip()
            device.next_user = ''
            if device.device_status == '1':
                if request.POST.get('device_user')  and request.POST.get('expired_date') :

                    device.device_user = UserProfile.objects.filter(id=request.POST.get('device_user', 0)).first()
                    device.expired_date = request.POST.get('expired_date').strip()
                else:
                    return render(request, 'devices/device_add.html', {'msg': '请输入用户和使用时间'})
            else:
                device.device_user = UserProfile.objects.filter(id=0).first()
                device.expired_date = date(3020,1,1)


            #device.device_type = DeviceType.objects.filter(id=request.POST.get('device_type')).first()
            #device.device_id = request.POST.get('device_id').strip()




            device.save()

            deviceLog(device,status_pre,device.device_status,user_pre,device.device_user)

            # user_name = device.device_user.username if device.device_user else ''
            #
            # # 该记录添加到历史表中
            # device_his = DeviceHis(deviceid=device.id, device_type=device.device_type.device_type, device_id=device.device_id,
            #                        device_mac=device.device_mac, device_root=device.device_root, device_status=device.device_status, device_user=device.device_user,
            #                        comment=device.comment)
            # device_his.save()

            # 将操作记录添加到日志中
            # new_log = UserOperateLog(username=request.user.username, scope=device.device_type, type='修改',
            #                          content=device_id)
            # new_log.save()
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
        # new_log = UserOperateLog(username=request.user.username, scope=device.device_type, type='删除',
        #                          content=str(device_id))
        # new_log.save()
        return HttpResponseRedirect((reverse('devices:device_list')))

class DeviceImportView(LoginRequiredMixin, View):


    def post(self,request):
        dict_root = {'是': '1', '否': '0'}
        dict_status = {'空闲': '0', '占用': '1', '损坏': '-1','':'0'}
        form = UploadExcelForm(request.POST,request.FILES)
        if form.is_valid():
            wb = xlrd.open_workbook(filename=None,file_contents=request.FILES['excel'].read())
            table = wb.sheets()[0]
            row  =table.nrows
            for i in range(1,row):

                col = table.row_values(i)
                device_type = str(col[1])
                device_id = str(col[3])
                device_root = dict_root[str(col[4])]
                department_name = str(col[5])
                device_user = str(col[6])

                device_status = dict_status[str(col[8])]


                #borrow_date = xlrd.xldate_as_datetime(col[7], 0).strftime('%Y-%m-%d') if device_status=='1' else None


                comment = str(col[9])
                device_sys = str(col[10])
                device_cpu = str(col[11])
                device_men = str(col[12])
                device_res = str(col[13])
                device_mac = str(col[14])
                try:
                    buy_time = xlrd.xldate_as_datetime(col[15],0).strftime('%Y-%m-%d')
                except:
                    buy_time=datetime.datetime.now()


                dev = Device.objects.filter(device_id=device_id)
                if not dev:

                    devicetype = DeviceType.objects.filter(device_type=device_type).first()

                    if devicetype:
                    #device_type = DeviceType.objects.filter(device_type=device_type).first()
                        pass
                    else:
                        print(device_type)
                        print(device_cpu)
                        print(device_res)
                        devicetype = DeviceType(device_type=device_type,device_cpu=device_cpu,device_res=device_res)
                        devicetype.save()


                    if device_status == '1':
                        department = Department.objects.filter(department_name=department_name).first()
                        if department:
                            pass
                        else:
                            department = Department(department_name = department_name)
                            department.save()

                        user = UserProfile.objects.filter(username=device_user).first()
                        if user:
                            pass
                        else:
                            user = UserProfile(username=device_user,department=department,password=make_password(pwd),isadmin='0',is_staff='1')
                            user.save()

                        device = Device(device_id=device_id,device_type=devicetype,buy_time=buy_time,
                                    device_mac=device_mac,device_sys=device_sys,device_root=device_root,device_men=device_men,
                                    device_status=device_status,device_user=user,comment=comment)
                        device.save()

                        deviceLog(device, '0', device_status, 0, device.device_user)
                    else:
                        admin_user = UserProfile.objects.filter(isadmin='1').first()
                        device = Device(device_type=devicetype, device_id=device_id, buy_time=buy_time,
                               device_mac=device_mac, device_root=device_root,device_sys=device_sys,device_men=device_men,
                               device_status=device_status, device_user=admin_user,comment=comment)
                        device.save()
                else:
                    pass

        return HttpResponseRedirect((reverse('devices:device_list')))
# # 设备列表导出
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

def deviceLog(device_id,stat_pre,stat,current_user,next_user):
    """
    case1:空闲->占用  损坏->占用   device  admin -> next_user
    case2:占用->空闲  占用->损坏   device  current_user-> admin
    case3:空闲->损坏  损坏->空闲   device
    case4:占用->占用              device  current_user-> next_user
    """

    def create_log():
        device_log = DeviceHis(device_id=device_id, device_user=next_user, start_time=datetime.datetime.now(), is_going='1')
        device_log.save()

    def modify_log():
        device_log = DeviceHis.objects.filter(device_id=device_id, device_user=current_user, is_going='1').first()
        if device_log:
            device_log.end_time = datetime.datetime.now()
            device_log.is_going = '0'
            device_log.save()

    if stat_pre =='0' or stat_pre=='-1':
        if stat =='1': #case1 新建一条记录
            create_log()

    if stat_pre  == '1':
        if stat =='0' or stat=='-1': #修改开始记录
            modify_log()

        else:
            modify_log()
            create_log()

class DeviceMyListView(View):
    def get(self, request):
        current_user = request.user

        devices = Device.objects.filter(Q(device_user=current_user)|Q(next_user=current_user.username))



        # 分页功能实现
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(devices, per_page=per_page, request=request)
        p_devices = p.page(page)
        print(p_devices)
        start = (int(page)-1) * per_page  # 避免分页后每行数据序号从1开始
        return render(request, 'devices/device_my.html', {'p_devices': p_devices,'start': start, 'num':len(devices),
                                                          'current_user':current_user})

class DeviceSelectNameView(LoginRequiredMixin, View):
    def get(self, request,device_id):
        current_user = request.user
        users = UserProfile.objects.filter(~Q(username=current_user) & Q(isadmin='0'))

        return render(request, 'devices/select_user.html', {'users': users,'device_id':device_id})

    def post(self, request,device_id):

        device_id = device_id

        device_user = request.POST.get('device_user').strip()
        user_name = UserProfile.objects.filter(id=device_user).first()
        device = Device.objects.filter(id=device_id).first()
        device.next_user = user_name.username
        device.save()

        return HttpResponseRedirect((reverse('devices:device_mylist')))

class DeviceSelectTimeView(LoginRequiredMixin, View):
    def get(self, request,device_id):

        return render(request, 'devices/select_time.html', {'device_id':device_id})

    def post(self, request,device_id):

        user = request.user
        device_id = device_id
        expired_date = request.POST.get('expired_date').strip()

        device = Device.objects.filter(id=device_id).first()
        pre_user = device.device_user
        print(pre_user)
        device.device_user = user
        device.next_user = ''
        device.expired_date = expired_date
        device.save()

        deviceLog(device, '1', '1', pre_user, user)

        return HttpResponseRedirect((reverse('devices:device_mylist')))