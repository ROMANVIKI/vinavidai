from django.contrib import admin
from .models import CustomUser, StaffMembership


# Register your models here
admin.site.register(CustomUser)
admin.site.register(StaffMembership)
