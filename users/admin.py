from django.contrib import admin
from . import models

# Register your models here.


class UserAdmin(admin.ModelAdmin):
     fields = ['name', 'surname', 'email', 'activation_code', 'password', 'is_active', ]


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Patient)
admin.site.register(models.Doctor)
admin.site.register(models.WorkDay)
admin.site.register(models.WorkBlock)