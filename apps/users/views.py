from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q
import django_excel as excel
from pure_pagination import Paginator, PageNotAnInteger


from .models import UserProfile,Department
from .forms import LoginForm, UserPwdModifyForm, UserInfoForm, DepartmentInfoForm
from device_sys.settings import per_page
from utils.mixin_utils import LoginRequiredMixin

# 定义普通用户初始密码
pwd = '123456'


# 定义用户的相关视图
# 用户登录
class UserLoginView(View):
    def get(self, request):
        return render(request, 'users/login.html')

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get('username').strip()
            pass_word = request.POST.get('password').strip()
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return render(request, 'users/login.html', {'msg': '账号或密码错误'})
        else:
            return render(request, 'users/login.html', {'msg': '账号或密码错误', 'login_form': login_form})


# 用户退出
class UserLogoutView(View):
    def get(self, request):
        logout(request)
        response = redirect(reverse('users:user_login'))
        response.delete_cookie('username')
        return response


# 用户修改密码
class UserPwdModifyView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'users/user_pwd_modify.html')

    def post(self, request):
        user_pwd_modify_form = UserPwdModifyForm(request.POST)
        if user_pwd_modify_form.is_valid():
            user = UserProfile.objects.get(username=request.user.username)
            pwd1 = request.POST.get('pwd1').strip()
            pwd2 = request.POST.get('pwd2').strip()
            if pwd1 == pwd2:
                user.password = make_password(pwd1)
                user.save()
                return HttpResponseRedirect((reverse('users:user_login')))
            else:
                return render(request, 'users/user_pwd_modify.html', {'msg': '两次密码不一致！'})
        else:
            return render(request, 'users/user_pwd_modify.html', {'msg': '密码不能为空！',
                                                                  'user_pwd_modify_form': user_pwd_modify_form})


# 管理员对用户的操作相关视图(管理员可见)
# 用户列表
class UserListView(LoginRequiredMixin, View):
    def get(self, request):
        search = request.GET.get('search')
        if search:
            search = request.GET.get('search').strip()
            users = UserProfile.objects.filter(Q(username__icontains=search) | Q(department__department_name__icontains=search),
                                               is_superuser=0).order_by('-is_staff')
        else:
            users = UserProfile.objects.filter(is_superuser=0).order_by('-is_staff')

        # 分页功能实现
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(users, per_page=per_page, request=request)
        p_users = p.page(page)
        start = (int(page)-1) * per_page  # 避免分页后每行数据序号从1开始
        return render(request, 'users/user_list.html', {'p_users': p_users, 'start': start, 'search': search})


# 用户添加
class UserAddView(LoginRequiredMixin, View):
    def get(self, request):
        departments = Department.objects.all()
        return render(request, 'users/user_add.html',{'department_lists':departments})

    def post(self, request):
        userinfo_form = UserInfoForm(request.POST)
        #print(userinfo_form)
        if userinfo_form.is_valid():
            username = request.POST.get('username').strip()
            department = Department.objects.filter(id=request.POST.get('department',0)).first()
            seat = request.POST.get('seat').strip()
            mobile = request.POST.get('mobile').strip()
            email = request.POST.get('email').strip()
            isadmin = request.POST.get('isadmin')
            user = UserProfile.objects.filter(username=username)
            if user:
                return render(request, 'users/user_add.html', {'msg': '用户 '+username+' 已存在！'})
            else:
                new_user = UserProfile(username=username, password=make_password(pwd), department=department,
                                       seat=seat, mobile=mobile, email=email, isadmin=isadmin)
                new_user.save()
                return HttpResponseRedirect((reverse('users:user_list')))
        else:
            return render(request, 'users/user_add.html', {'msg': '输入错误！', 'userinfo_form': userinfo_form})


# 用户详情
class UserDetailView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        departments = Department.objects.all()
        user = UserProfile.objects.get(id=user_id)
        return render(request, 'users/user_detail.html', {'user': user,'department_lists': departments})


# 用户修改
class UserModifyView(LoginRequiredMixin, View):

    def post(self, request):
        userinfo_form = UserInfoForm(request.POST)
        user_id = int(request.POST.get('user_id'))
        user = UserProfile.objects.get(id=user_id)



        if userinfo_form.is_valid():
            username = request.POST.get('username').strip()
            other_user = UserProfile.objects.filter(~Q(id=user_id), username=username)
            # 如果修改了用户名，判断是否该用户名与其他用户冲突
            if other_user:
                return render(request, 'users/user_detail.html', {'user': user, 'msg': username+'用户名已存在！'})
            else:
                user.username = request.POST.get('username').strip()
                user.department = Department.objects.filter(id=request.POST.get('department',0)).first()
                user.seat = request.POST.get('seat').strip()
                user.mobile = request.POST.get('mobile').strip()
                user.email = request.POST.get('email').strip()
                user.isadmin = request.POST.get('isadmin')
                user.is_staff = request.POST.get('is_staff')
                user.save()
                return HttpResponseRedirect((reverse('users:user_list')))
        else:
            return render(request, 'users/user_detail.html', {'user': user, 'msg': '输入错误！',
                                                              'userinfo_form': userinfo_form})


# 重置用户密码
class UserResetPwd(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = UserProfile.objects.get(id=user_id)
        user.password = make_password(pwd)
        user.save()
        return HttpResponseRedirect((reverse('users:user_list')))


# 用户删除
class UserDeleteView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = UserProfile.objects.get(id=user_id)
        user.delete()
        return HttpResponseRedirect((reverse('users:user_list')))


# 用户导出
class UserExportView(LoginRequiredMixin, View):
    def get(self, request):
        search = request.GET.get('search')
        if search:
            search = request.GET.get('search').strip()
            users = UserProfile.objects.filter(Q(username__icontains=search) | Q(staff_no__icontains=search)
                                               | Q(department__icontains=search) | Q(seat__icontains=search)
                                               | Q(mobile__icontains=search) | Q(email__icontains=search,
                                               is_superuser=0)).order_by('-is_staff')
        else:
            users = UserProfile.objects.filter(is_superuser=0).order_by('-is_staff')
        columns_names = ['id', 'username', 'staff_no', 'department', 'seat', 'mobile', 'email', 'is_staff']
        return excel.make_response_from_query_sets(users, columns_names, 'xls', file_name='人员列表')


# 操作日志视图(所有用户可见)
# class UserOperateView(LoginRequiredMixin, View):
#     def get(self, request):
#         search = request.GET.get('search')
#         if search:
#             search = search.strip().upper()
#             operate_logs = UserOperateLog.objects.filter(Q(username__icontains=search) | Q(scope__icontains=search)
#                                                          | Q(type__icontains=search)).order_by('-modify_time')
#         else:
#             operate_logs = UserOperateLog.objects.all().order_by('-modify_time')
#
#         # 分页功能实现
#         try:
#             page = request.GET.get('page', 1)
#         except PageNotAnInteger:
#             page = 1
#         p = Paginator(operate_logs, per_page=per_page, request=request)
#         p_operate_logs = p.page(page)
#         start = (int(page)-1) * per_page  # 避免分页后每行数据序号从1开始
#
#         return render(request, 'users/operate_log.html', {'operate_logs': p_operate_logs, 'start': start,
#                                                           'search': search})

class DepartmentListView(LoginRequiredMixin,View):
    def get(self, request):
        search = request.GET.get('search')
        if search:
            search = request.GET.get('search').strip()
            departments = Department.objects.filter(Q(department_name__icontains=search))
        else:
            departments = Department.objects.all()

        # 分页功能实现
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(departments, per_page=per_page, request=request)
        p_departments = p.page(page)
        start = (int(page) - 1) * per_page  # 避免分页后每行数据序号从1开始

        return render(request, 'users/department_list.html', {'p_departments': p_departments, 'start': start, 'search': search})

class DepartmentAddView(LoginRequiredMixin,View):
    def get(self, request):
        return render(request, 'users/department_add.html')

    def post(self, request):
        department_form = DepartmentInfoForm(request.POST)
        if department_form.is_valid():
            department_name = request.POST.get('department_name').strip()

            user = Department.objects.filter(department_name=department_name)
            if user:
                return render(request, 'users/department_add.html', {'msg': '部门 ' + department_name + ' 已存在！'})
            else:
                new_department = Department(department_name=department_name)
                new_department.save()
                return HttpResponseRedirect((reverse('users:department_list')))
        else:
            return render(request, 'users/department_add.html', {'msg': '输入错误！', 'department_form': department_form})

class DepartmentDetailView(LoginRequiredMixin,View):
    def get(self,request,department_id):
        dep = Department.objects.get(id=department_id)
        return render(request, 'users/department_modify.html', {'department': dep})


class DepartmentModifyView(LoginRequiredMixin,View):
    # def get(self, request,department_id):
    #     dep = Department.objects.get(id=department_id)
    #     return render(request,'users/department_modify.html', {'department': dep})
    #     return HttpResponseRedirect(reverse('users:department_modify'),department=dep)
    def post(self, request):
        department_form = DepartmentInfoForm(request.POST)
        department_id = int(request.POST.get('department_id'))
        #print("dep id is:",department_id)
        department = Department.objects.get(id=department_id)
        if department_form.is_valid():
            department_name = request.POST.get('department_name').strip()
            other_dep = Department.objects.filter(~Q(id=department_id), department_name=department_name)
            # 如果修改，判断是否冲突
            if other_dep:
                return render(request, 'users/department_modify.html', {'department': department, 'msg': department_name + '已存在！'})
            else:
                department.department_name = request.POST.get('department_name').strip()

                department.save()
                return HttpResponseRedirect((reverse('users:department_list')))
        else:
            return render(request, 'users/department_modify.html', {'department': department, 'msg': '输入错误！',
                                                              'department_form': department_form})

class DepartmentDeleteView(LoginRequiredMixin,View):
    def get(self, request, department_id):
        department = Department.objects.get(id=department_id)
        department.delete()
        return HttpResponseRedirect((reverse('users:department_list')))

# 定义全局404
def page_not_found(request):
    response = render('404.html')
    response.status_code = 404
    return response


# 定义全局500
def page_error(request):
    response = render('500.html')
    response.status_code = 500
    return response

