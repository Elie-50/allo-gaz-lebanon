from django.urls import path
from .views import OrderDetailView, MarkOrdersDeliveredAPIView, GenerateReceiptAPIView

urlpatterns = [
    path('', OrderDetailView.as_view(), name='add-order'),
    path('<int:pk>/', OrderDetailView.as_view(), name='edit-order'),
    path('mark-delivered/', MarkOrdersDeliveredAPIView.as_view(), name='mark-orders-delivered'),
    path('receipt/<int:address_id>/<str:date_str>/<int:driver_id>/', GenerateReceiptAPIView.as_view(), name='generate_receipt'),
]
