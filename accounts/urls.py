from django.urls import path
from .views import LoginView, LogoutView, RefreshTokenView, UserDetailView,RegisterManagerView


urlpatterns = [
    path('register-manager/', RegisterManagerView.as_view(), name='register-manager'),  
    path('login/',LoginView.as_view(), name='login'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('refresh/',RefreshTokenView.as_view(), name='refresh'),
    path('user/',UserDetailView.as_view(), name='refresh'),
]