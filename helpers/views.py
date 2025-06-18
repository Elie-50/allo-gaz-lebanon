from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from graphene_django.views import GraphQLView

class BaseView(APIView):
    Serializer = None
    Model = None

    def check_user_is_active(self, user):
        """
        A helper function to check if the user is active.
        """
        if not user.is_active:
            raise AuthenticationFailed("Access Denied")

    def get_object(self, pk):
        """
        A helper function to retrieve the object by primary key.
        This will be used for GET, PUT, and DELETE operations.
        """
        return get_object_or_404(self.Model, pk=pk)

    def handle_soft_delete(self, obj):
        """
        A utility method to handle soft deletion by checking `isActive` or `is_active` attributes.
        """
        if hasattr(obj, 'isActive'):
            obj.isActive = False
        elif hasattr(obj, 'is_active'):
            obj.is_active = False
        else:
            obj.delete()  # Fallback to hard delete if no soft delete field is found
        
        obj.save()

    def post(self, request, *args, **kwargs):
        self.check_user_is_active(request.user)

        serializer = self.Serializer(data=request.data, context={'request': request}, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        self.check_user_is_active(request.user)

        obj = self.get_object(pk)
        serializer = self.Serializer(obj, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        self.check_user_is_active(request.user)

        obj = self.get_object(pk)
        self.handle_soft_delete(obj)
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class DRFJWTGraphQLView(GraphQLView):
    def get_context(self, request):
        context = super().get_context(request)
        jwt_auth = JWTAuthentication()
        
        try:
            user_auth_tuple = jwt_auth.authenticate(request)
            if user_auth_tuple is not None:
                request.user, _ = user_auth_tuple
            else:
                request.user = None
        except AuthenticationFailed:
            pass
        
        return context
