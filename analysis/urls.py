from django.urls import path
from analysis.views import *


app_name = 'analysis'
urlpatterns = [
    path('analysis/', analysis, name='analysis'),
    path('chart/', chart, name='chart'),
]
