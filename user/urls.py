from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserDetailView, CustomTokenObtainPairView, UserView

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('', UserView.as_view(), name='user-detail'),
    path('create/', UserDetailView.as_view(), name='add-user'),
    path('<int:pk>/', UserDetailView.as_view(), name='edit-user'),
]
