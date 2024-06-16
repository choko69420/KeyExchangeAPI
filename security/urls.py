from django.urls import path, include
from rest_framework.authtoken import views
from django.contrib import admin
from .views import ChannelViewSet, SecretExchangeView, KeyGenerationView
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'channels', ChannelViewSet, basename='channels')
urlpatterns = [
	path('', include(router.urls)),
	path('setsecret', SecretExchangeView.as_view(), name='setsecret'),
	path('generatekey', KeyGenerationView.as_view(), name='generatekey'),
]
