from django.urls import path

from .views import qrcode_generator

app_name = 'qrcode_generator'


urlpatterns = [
    path('', qrcode_generator,
         name='qrcode_generator'),
]
