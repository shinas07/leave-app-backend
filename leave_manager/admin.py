from django.contrib import admin
from .models import LeaveRequest,YearlyLeaveBalance
# Register your models here.

admin.site.register(LeaveRequest)
admin.site.register(YearlyLeaveBalance)