from django.urls import path
from .views import CustomerDetailView, AddressDetailView, PhoneNumberDetailView

urlpatterns = [
    path('', CustomerDetailView.as_view(), name='customer-list'),
    path('<int:pk>/', CustomerDetailView.as_view(), name='customer-detail'),
    path('address/', AddressDetailView.as_view(), name='add-address'),
    path('address/<int:pk>/', AddressDetailView.as_view(), name='edit-address'),
    path('address/phone-number/', PhoneNumberDetailView.as_view(), name='add-phone-number'),
    path('address/phone-number/<int:pk>/', PhoneNumberDetailView.as_view(), name='edit-phone-number')
]