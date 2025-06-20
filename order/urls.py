from django.urls import path
from .views import OrderDetailView, MarkOrdersDeliveredAPIView, GenerateReceiptAPIView, ItemSalesSummaryView

urlpatterns = [
    path('', OrderDetailView.as_view(), name='add-order'),
    path('sales/', ItemSalesSummaryView.as_view(), name='item-sales-summary'),
    path('<int:pk>/', OrderDetailView.as_view(), name='edit-order'),
    path('mark-delivered/', MarkOrdersDeliveredAPIView.as_view(), name='mark-orders-delivered'),
    path('receipt/<int:address_id>/<str:date_str>/<int:driver_id>/', GenerateReceiptAPIView.as_view(), name='generate_receipt'),
]
