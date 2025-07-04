from .models import User
from .serializers import UserSerializer, CustomTokenObtainPairSerializer
from helpers.views import BaseView
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from helpers.permissions import IsSuperUser


class UserDetailView(BaseView):
    permission_classes = [IsSuperUser]
    
    Serializer = UserSerializer
    Model = User

class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Access the authenticated user
        user = request.user
        
        # Serialize the user data
        serializer = UserSerializer(user)
        
        # Return the serialized data in the response
        return Response(serializer.data, status=status.HTTP_200_OK)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer