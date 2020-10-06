from django.contrib import admin

from django.contrib import admin

from .models import UserProfile, Department


class UserProfileAdmin(admin.ModelAdmin):
    search_fileds = ['username','department__department_name']



class DepartmentAdmin(admin.ModelAdmin):
    pass

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Department, DepartmentAdmin)