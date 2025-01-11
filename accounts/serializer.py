from rest_framework import serializers
from accounts.models import User  # Replace with the path to your User model

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'user_type'] 
        