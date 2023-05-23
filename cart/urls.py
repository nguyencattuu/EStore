from django.urls import path
from cart.views import *


app_name = 'cart'
urlpatterns = [
    path('gio-hang/', gio_hang, name='gio_hang'),
    path('mua-ngay/<int:product_id>/', mua_ngay, name='mua_ngay'),
    # http://127.0.0.1:8000/mua-ngay/186/
    path('xoa-san-pham/<int:product_id>/', xoa_san_pham, name='xoa_san_pham'),
    path('thanh-toan/', thanh_toan, name='thanh_toan'),
    path('them-vao-gio-hang/<int:product_id>/', them_vao_gio_hang, name='them_vao_gio_hang'),
]
