from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .serializer import UserSerializer
from accounts.models import User


class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self,request):
        email = request.data.get('email')
        password = request.data.get('password')
        user_type = request.data.get('userType')
        if not email or not password or not user_type:
            return Response({'error':'Pleace provide all details'},status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response({'error':'Invalid credentials'}, status=status.HTTP_403_FORBIDDEN)
        
        if not user.is_active:
            return Response(
                {'error': 'Your account has been blocked. Please contact your manager.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if user.user_type != user_type:
            return Response({
                'error':f'Invaild user type. User are not a {user_type}'}, status=status.HTTP_403_FORBIDDEN
            )
        
        user = User.objects.get(email=email)
        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            serializer = UserSerializer(user)
        else:
            return Response({'error':'user not found'},status=status.HTTP_401_UNAUTHORIZED)
        return Response({
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'user': serializer.data,
            
        }, status=status.HTTP_200_OK)
    
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Failed to fetch user details"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"success": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Invalid refresh token or logout failed'}, status=status.HTTP_400_BAD_REQUEST)
    

class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            print('not refresh token')
            return Response({'error': 'Refresh token not found'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({'access': access_token}, status=status.HTTP_200_OK)
        except Exception as e:
            print(str(e))
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)