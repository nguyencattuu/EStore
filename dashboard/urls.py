from django.urls import path
from dashboard.views import *


app_name = 'dashboard'
urlpatterns = [
    path('dashboard/', dashboard_with_pivot, name='dashboard'),
    path('pivot-data/', pivot_data, name='pivot_data'),
]
