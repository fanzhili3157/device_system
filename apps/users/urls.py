from django.urls import path

from .views import UserLoginView, UserLogoutView
from .views import UserListView, UserAddView, UserDetailView, UserModifyView, UserResetPwd, UserDeleteView
from .views import UserPwdModifyView, UserExportView
from .views import DepartmentListView,DepartmentAddView,DepartmentModifyView,DepartmentDeleteView,DepartmentDetailView

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('logout/', UserLogoutView.as_view(), name='user_logout'),

    # 定义用户的相关url
    path('user/list/', UserListView.as_view(), name='user_list'),
    path('user/add/', UserAddView.as_view(), name='user_add'),
    path('user/detail/<int:user_id>/', UserDetailView.as_view(), name='user_detail'),
    path('user/modify/', UserModifyView.as_view(), name='user_modify'),
    path('user/pwdreset/<int:user_id>', UserResetPwd.as_view(), name='user_pwdreset'),   #  该url为管理员重置用户密码
    path('user/delete/<int:user_id>/', UserDeleteView.as_view(), name='user_delete'),
    path('user/export/', UserExportView.as_view(), name='user_export'),
    path('user/pwdmodify/', UserPwdModifyView.as_view(), name='user_pwd_modify'),  #  该url为用户修改自身密码

    #部门相关url
    path('department/list/', DepartmentListView.as_view(), name='department_list'),
    path('department/add/',DepartmentAddView.as_view(),name='department_add'),
    path('department/detial/<int:department_id>/',DepartmentDetailView.as_view(),name='department_detail'),
    path('department/modify/',DepartmentModifyView.as_view(),name='department_modify'),
    path('department/delete/<int:department_id>',DepartmentDeleteView.as_view(),name='department_delete'),


    # 定义操作日志url
    #path('user/operate_log/', UserOperateView.as_view(), name='operate_log'),
]
