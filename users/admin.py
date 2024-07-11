from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.User)
admin.site.register(models.Patient)
admin.site.register(models.Doctor)
admin.site.register(models.WorkDay)
admin.site.register(models.WorkBlock)