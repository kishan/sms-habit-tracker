from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # Twilio URLs
    path('receive_sms/', views.receive_sms, name='receive_sms'),
    path('sms_test/', views.sms_test, name='sms_test'),
    path('sms_test/morning', views.sms_test_morning_reminder, name='morning_reminder'),
]