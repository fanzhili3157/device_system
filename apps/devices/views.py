from django.shortcuts import render
from django.views.generic.base import View
from django.http.response import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db.models import Q, Count
from pure_pagination import Paginator, PageNotAnInteger
import csv

from .models import Device, DeviceType, DeviceHis
from .forms import DeviceForm, DeviceTypeForm
from users.models import UserOperateLog, UserProfile
from zcgl.settings import per_page
from utils.mixin_utils import LoginRequiredMixin


# 定义首页视图
class IndexView(View):
    def get(self, request):
        pass
#        total = Server.objects.count()
#        device_groups = Server.objects.values("zctype__zctype").annotate(zctype_num=Count("zctype")).all().\
#            order_by('-zctype_num', 'zctype__zctype')
#        return render(request, 'servers/index.html', {'zctype_groups': device_groups, 'total': total})


# 资产列表
class ServerListView(View):
    def get(self, request):
        search = request.GET.get('search')
        if search:
            search = request.GET.get('search').strip()
            # 如果输入的是纯数字，则将序号也加入到搜索的列表中来
            try:
                search_int = int(search)
                servers = Device.objects.filter(Q(id=search_int) | Q(device_type__device_type__icontains=search)
                                                | Q(device_brand__icontains=search) | Q(device_id__icontains=search)
                                                | Q(device_user__icontains=search) | Q(device_status__icontains=search)
                                                | Q(device_type__system__icontains=search) | Q(device_type__cpu__icontains=search)
                                                | Q(device_type__men__icontains=search) | Q(device_type__res__icontains=search)). \
                    order_by('device_type', 'id')
            except Exception:
                servers = Device.objects.filter(Q(device_type__device_type__icontains=search)
                                                | Q(device_brand__icontains=search) | Q(device_id__icontains=search)
                                                | Q(device_user__icontains=search) | Q(device_status__icontains=search)
                                                | Q(device_type__system__icontains=search) | Q(device_type__cpu__icontains=search)
                                                | Q(device_type__men__icontains=search) | Q(device_type__res__icontains=search)). \
                    order_by('device_type', 'id')
        else:
            servers = Device.objects.all().order_by('device_type', 'id')

        # 分页功能实现
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(servers, per_page=per_page, request=request)
        p_servers = p.page(page)
        start = (int(page)-1) * per_page  # 避免分页后每行数据序号从1开始
        return render(request, 'servers/server_list.html', {'p_servers': p_servers, 'start': start, 'search': search})


# 资产添加
class ServerAddView(LoginRequiredMixin, View):
    def get(self, request):
        users = UserProfile.objects.filter(is_superuser=0, is_staff='1')
        device_types = DeviceType.objects.all()
        return render(request, 'servers/server_add.html', {'users': users, 'server_types': device_types})

    def post(self, request):
        device_type = DeviceType.objects.filter(id=request.POST.get('device_type', 0)).first()
        device_user = UserProfile.objects.filter(id=request.POST.get('device_user', 0)).first()
        device_id = request.POST.get('device_id').strip()
        device_mac = request.POST.get('device_mac').strip()

        device_root = request.POST.get('device_root')
        device_status = request.POST.get('device_status').strip()
        comment = request.POST.get('comment').strip()

        server_form = DeviceForm(request.POST)
        # 判断表单是否正确
        if server_form.is_valid():
            new_server = Device(device_type=device_type, device_id=device_id, device_mac=device_mac, device_root=device_root,
                                device_status=device_status, device_user=device_user,comment=comment)
            new_server.save()

            user_name = device_user.username if device_user else ''

            # 该记录添加到历史表中
            server_his = DeviceHis(serverid=new_server.id, device_type=device_type.device_type, device_id=device_id,
                                   device_mac=device_mac, device_root=device_root, device_status=device_status, device_user=device_user,
                                   comment=comment)
            server_his.save()

            # 将操作记录添加到日志中
            new_log = UserOperateLog(username=request.user.username, scope=device_type.device_type, type='增加',
                                     content=server_his.serverid)
            new_log.save()
            return HttpResponseRedirect((reverse('servers:server_list')))
        else:
            users = UserProfile.objects.filter(is_superuser=0)
            server_types = DeviceType.objects.all()
            return render(request, 'servers/server_add.html', {'msg': '输入错误！', 'users': users,
                                                               'server_form': server_form, 'server_types': server_types})


# 资产详情
class ServerDetailView(LoginRequiredMixin, View):
    def get(self, request, server_id):
        server = Device.objects.filter(id=server_id).first()
        users = UserProfile.objects.filter(is_superuser=0, is_staff='1')
        server_types = DeviceType.objects.all()
        server_hiss = DeviceHis.objects.filter(serverid=server_id).order_by('-modify_time')

        # 分页功能实现
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(server_hiss, per_page=per_page, request=request)
        p_server_hiss = p.page(page)
        start = (int(page)-1) * per_page  # 避免分页后每行数据序号从1开始
        return render(request, 'servers/server_detail.html', {'users': users, 'server': server,
                                                              'server_types': server_types,
                                                              'p_server_hiss': p_server_hiss, 'start': start})


# 资产修改
class ServerModifyView(LoginRequiredMixin, View):
    def post(self, request):
        server_id = int(request.POST.get('server_id'))
        server = Device.objects.filter(id=server_id).first()
        server_form = DeviceForm(request.POST)
        # 判断表单是否正确
        if server_form.is_valid():
            server.device_type = DeviceType.objects.filter(id=request.POST.get('device_type')).first()
            server.device_id = request.POST.get('device_id').strip()
            server.device_status = request.POST.get('device_status').strip()
            server.brand = request.POST.get('brand').strip()
            server.buy_time = request.POST.get('buy_time').strip()
            server.device_mac = request.POST.get('device_mac').strip()
            server.device_root = request.POST.get('device_root').strip()
            server.device_user = UserProfile.objects.filter(id=request.POST.get('device_user', 0)).first()
            server.comment = request.POST.get('comment').strip()
            server.save()

            user_name = server.device_user.username if server.owner else ''

            # 该记录添加到历史表中
            server_his = DeviceHis(serverid=server.id, device_type=server.device_type.device_type, device_id=server.device_id,
                                   device_mac=server.device_mac, device_root=server.device_root, device_status=server.device_status, device_user=server.device_user,
                                   comment=server.comment)
            server_his.save()

            # 将操作记录添加到日志中
            new_log = UserOperateLog(username=request.user.username, scope=server.device_type, type='修改',
                                     content=server_id)
            new_log.save()
            return HttpResponseRedirect((reverse('servers:server_list')))
        else:
            users = UserProfile.objects.filter(is_superuser=0, is_staff='1')
            server_types = DeviceType.objects.all()
            return render(request, 'servers/server_detail.html', {'users': users, 'server': server,
                                                                  'server_types': server_types,
                                                                  'msg': '输入错误！', 'server_form': server_form})


# 资产删除
class ServerDeleteView(LoginRequiredMixin, View):
    def get(self, request, server_id):
        server = Device.objects.get(id=server_id)
        scope = server.zctype
        user_name = server.owner.username if server.owner else ''

        # 该记录添加到历史表中
        server_his = DeviceHis(serverid=server.id, device_type=server.device_type.device_type, device_id=server.device_id,
                                   device_mac=server.device_mac, device_root=server.device_root, device_status=server.device_status, device_user=server.device_user,
                               comment='该记录被删除')
        server_his.save()

        # 删除该记录
        server.delete()

        # 将操作记录添加到日志中
        new_log = UserOperateLog(username=request.user.username, scope=scope, type='删除',
                                 content=str(server_id))
        new_log.save()
        return HttpResponseRedirect((reverse('servers:server_list')))


# 资产列表导出
class ServerExportView(LoginRequiredMixin, View):
    def get(self, request):
        search = request.GET.get('search')
        if search:
            search = request.GET.get('search').strip()
            servers = Device.objects.filter(Q(zctype__zctype__icontains=search) | Q(ipaddress__icontains=search)
                                            | Q(description__icontains=search) | Q(brand__icontains=search)
                                            | Q(zcmodel__icontains=search) | Q(zcnumber__icontains=search)
                                            | Q(zcpz__icontains=search) | Q(owner__username__icontains=search)).\
                order_by('zctype')
        else:
            servers = Device.objects.all().order_by('zctype')
        servers = servers.values('id', 'zctype__zctype', 'ipaddress', 'description', 'brand', 'zcmodel', 'zcnumber',
                                 'zcpz', 'owner__username', 'undernet', 'guartime', 'comment')
        colnames = ['序号', '资产类型', 'IP地址', '功能描述', '设备品牌', '设备型号', '设备序号', '设备配置',
                    '管理人员', '所在网络', '保修期', '备注']
        response = create_excel(colnames, servers, 'zcgl')
        return response


def create_excel(columns, content, file_name):
    """创建导出csv的函数"""
    file_name = file_name + '.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + file_name
    response.charset = 'gbk'
    writer = csv.writer(response)
    writer.writerow(columns)
    for i in content:
        writer.writerow([i['id'], i['zctype__zctype'], i['ipaddress'], i['description'], i['brand'], i['zcmodel'],
                         i['zcnumber'], i['zcpz'], i['owner__username'], i['undernet'], i['guartime'], i['comment']])
    return response


# 资产类型列表
class TypeListView(LoginRequiredMixin, View):
    def get(self, request):
        server_types = DeviceType.objects.all()
        return render(request, 'servers/type_list.html', {'server_types': server_types})


# 资产类型添加
class TypeAddView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'servers/type_add.html', {})

    def post(self, request):
        device_type = request.POST.get('zctype').strip().upper()
        devicetype_form = DeviceTypeForm(request.POST)
        # 判断表单是否正确
        if devicetype_form.is_valid():
            other_servertype = DeviceType.objects.filter(device_type=device_type)
            # 判断是否已经存在了该zctype
            if other_servertype:
                return render(request, 'servers/type_add.html', {'msg': device_type+' 已存在！'})
            else:
                new_servertype = DeviceType(device_type=device_type)
                new_servertype.save()
                return HttpResponseRedirect((reverse('servers:type_list')))
        else:
            return render(request, 'servers/type_add.html', {'msg': '输入错误！', 'servertype_form': devicetype_form})


# 资产类型详情
class TypeDetailView(LoginRequiredMixin, View):
    def get(self, request, type_id):
        device_type = DeviceType.objects.get(id=type_id)
        return render(request, 'servers/type_detail.html', {'device_type': device_type})


# 资产类型修改
class TypeModifyView(LoginRequiredMixin, View):
    def post(self, request):
        type_id = int(request.POST.get('type_id'))
        device_type = request.POST.get('zctype').strip().upper()
        exist_device_type = DeviceType.objects.get(id=type_id)
        other_device_type = DeviceType.objects.filter(~Q(id=type_id), device_type=device_type)
        devicetype_form = DeviceTypeForm(request.POST)
        # 判断表单是否正确
        if devicetype_form.is_valid():
            # 如果修改了资产类型名字，判断是否该名字与其他资产类型名字冲突
            if other_device_type:
                return render(request, 'servers/type_detail.html', {'device_type': exist_device_type,
                                                                    'msg': device_type+' 已存在！'})
            else:
                exist_device_type.device_type = device_type
                exist_device_type.save()
                return HttpResponseRedirect((reverse('servers:type_list')))
        else:
            return render(request, 'servers/type_detail.html', {'device_type': exist_device_type,
                                                                'msg': '输入错误！',
                                                                'devicetype_form': devicetype_form})
