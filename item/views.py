from .serializers import ItemSerializer, SourceSerializer
from .models import Item, Source
from helpers.views import BaseView
from rest_framework.permissions import IsAdminUser, BasePermission

class IsSuperUser(BasePermission):
    """
    Allows access onlt to super users
    """
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)

class ItemDetailView(BaseView):
    permission_classes = [IsAdminUser]

    Serializer = ItemSerializer
    Model = Item


class SourceDetailView(BaseView):
    permission_classes = [IsSuperUser]

    Serializer = SourceSerializer
    Model = Source