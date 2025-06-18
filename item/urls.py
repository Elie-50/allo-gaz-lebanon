from django.urls import path
from .views import ItemDetailView, SourceDetailView

urlpatterns = [
    path('', ItemDetailView.as_view(), name='add-item'),
    path('<int:pk>/', ItemDetailView.as_view(), name='edit-item'),
    path('source/', SourceDetailView.as_view(), name='add-source'),
    path('source/<int:pk>/', SourceDetailView.as_view(), name='edit-source'),
]
