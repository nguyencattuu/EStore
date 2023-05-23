from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from store.models import Product
from django.core import serializers


# Create your views here.
# def dashboard(request):
#     return HttpResponse('Test dashboard')


def dashboard_with_pivot(request):
    return render(request, 'dashboard/dashboard_with_pivot.html', {})


def pivot_data(request):
    dataset = Product.objects.all()
    data = serializers.serialize('json', dataset)
    return JsonResponse(data, safe=False)


