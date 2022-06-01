from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # Twilio URLs
    path('sms_reply/', views.sms_reply, name='sms_reply'),
    path('sms_test/', views.sms_test, name='sms_test'),
]