from rest_framework import serializers
from .models import LeaveRequest
from accounts.models import User
from django.contrib.auth.password_validation import validate_password



# class LeaveRequestSerializer(serializers.ModelSerializer):
#     user_email = serializers.EmailField(source='user.email', read_only=True)
#     class Meta:
#         model = LeaveRequest
#         fields = ['id', 'user','user_email', 'leave_type', 'start_date', 'end_date', 'reason', 'status']
#         read_only_fields = ['user', 'status']

class LeaveRequestSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    class Meta:
        model = LeaveRequest
        fields = ['id', 'leave_type', 'start_date', 'end_date', 'reason', 'status', 'duration', 'created_at','user_email']
        read_only_fields = ['status', 'duration']

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id',  'email','username' , 'user_type']







class CreateEmployeeSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email',
            'user_type',
            'password',
            'confirm_password',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'user_type': {'default': 'employee'}
        }

    def validate(self, data):
        if data['password'] != data.pop('confirm_password'):
            raise serializers.ValidationError({
                "password": "Passwords don't match"
            })
        
        # Validate password strength
        validate_password(data['password'])
        
        # Set username to email if not provided
        if 'username' not in data:
            data['username'] = data['email']
            
        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)