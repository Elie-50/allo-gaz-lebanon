"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include, re_path
from django.views.decorators.csrf import csrf_exempt
from order.views import ExchangeRateView
from helpers.views import DRFJWTGraphQLView
from .views import ReactAppView, BackupDatabaseAPIView
import os


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/backup/', BackupDatabaseAPIView.as_view(), name='backup'),
    path('api/user/', include('user.urls')),
    path('api/order/', include('order.urls')),
    path('api/item/', include('item.urls')),
    path('api/customer/', include('customer.urls')),
    path('api/exchange-rate/', ExchangeRateView.as_view(), name='exchange-rate'),
    path("graphql/", csrf_exempt(DRFJWTGraphQLView.as_view(graphiql=True))),

]

# Serve static and media in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, "staticfiles"))

# Catch-all React route goes LAST
urlpatterns += [re_path(r"^(?!static/|media/|favicon\.ico$|robots\.txt$).*", ReactAppView.as_view(), name="react_app")]