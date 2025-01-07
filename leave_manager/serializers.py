from rest_framework import serializers
from .models import LeaveRequest

# class LeaveTypeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = LeaveType
#         fildes = '__all__'

class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['id', 'user', 'leave_type', 'start_date', 'end_date', 'reason', 'status']
        read_only_fields = ['user', 'status']