from django.urls import path
from customer.views import *


app_name = 'customer'
urlpatterns = [
    path('dang-nhap/', dang_nhap, name='dang_nhap'),
    path('dang-xuat/', dang_xuat, name='dang_xuat'),
    path('tai-khoan-cua-toi/', tai_khoan_cua_toi, name='tai_khoan_cua_toi'),
    path('xuat-bao-cao-don-hang/<int:pk>/', xuat_bao_cao_don_hang, name='xuat_bao_cao_don_hang'),
]
