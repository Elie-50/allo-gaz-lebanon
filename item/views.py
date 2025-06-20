from .serializers import ItemSerializer, SourceSerializer
from .models import Item, Source
from helpers.views import BaseView
from rest_framework.permissions import IsAdminUser
from helpers.permissions import IsSuperUser

class ItemDetailView(BaseView):
    permission_classes = [IsAdminUser]

    Serializer = ItemSerializer
    Model = Item


class SourceDetailView(BaseView):
    permission_classes = [IsSuperUser]

    Serializer = SourceSerializer
    Model = Source