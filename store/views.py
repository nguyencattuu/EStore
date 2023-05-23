from django.shortcuts import render, reverse, redirect
from store.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from cart.cart import Cart
from django.http import JsonResponse
from rest_framework import viewsets, permissions
from store.serializers import ProductSerializer
from urllib.parse import urlencode
from cart.views import them_vao_gio_hang
from django.conf import settings
import feedparser
import os
import pandas as pd
import re


# Load thông tin Brands
brands = Brand.objects.all()

# Load danh sách subcategory ra màn hình
subcategories = SubCategory.objects.order_by('name')


# Create your views here.
def trang_chu(request):
    cart = Cart(request)

    # Load thông tin Slider
    sliders = Slider.objects.all()

    # Thiết bị gia đình => id = 1
    subcategory_id_tbgd = SubCategory.objects.filter(category=1).values('id')    # <QuerySet [{'id': 1}, {'id': 2}, {'id': 3}, {'id': 4}, {'id': 5}]>
    list_subcategory_id_tbgd = [sub_id['id'] for sub_id in subcategory_id_tbgd]  # List comprehension => [1, 2, 3, 4, 5]
    products_tbgd = Product.objects.filter(subcategory__in=list_subcategory_id_tbgd).order_by('-public_day')[:20]

    # Đồ dùng nhà bếp => id = 2
    subcategory_id_ddnb = SubCategory.objects.filter(category=2).values('id')  
    list_subcategory_id_ddnb = [sub_id['id'] for sub_id in subcategory_id_ddnb]
    products_ddnb = Product.objects.filter(subcategory__in=list_subcategory_id_ddnb).order_by('-public_day')[:20]

    return render(request, 'store/index.html', {
        'sliders': sliders,
        'brands': brands,
        'products_tbgd': products_tbgd,
        'products_ddnb': products_ddnb,
        'cart': cart,
    })


def trang_chu_2(request):
    cart = Cart(request)

    # Load thông tin Slider
    sliders = Slider.objects.all()

    # Thiết bị gia đình => id = 1
    subcategory_id_tbgd = SubCategory.objects.filter(category=1).values('id')    # <QuerySet [{'id': 1}, {'id': 2}, {'id': 3}, {'id': 4}, {'id': 5}]>
    list_subcategory_id_tbgd = [sub_id['id'] for sub_id in subcategory_id_tbgd]  # List comprehension => [1, 2, 3, 4, 5]
    products_tbgd = Product.objects.filter(subcategory__in=list_subcategory_id_tbgd).order_by('-public_day')[:20]

    # Đồ dùng nhà bếp => id = 2
    subcategory_id_ddnb = SubCategory.objects.filter(category=2).values('id')  
    list_subcategory_id_ddnb = [sub_id['id'] for sub_id in subcategory_id_ddnb]
    products_ddnb = Product.objects.filter(subcategory__in=list_subcategory_id_ddnb).order_by('-public_day')[:20]

    so_lan = 0
    if request.COOKIES.get('so_lan_truy_cap'):
        so_lan = int(request.COOKIES.get('so_lan_truy_cap'))

    response =  render(request, 'store/index_2.html', {
        'sliders': sliders,
        'brands': brands,
        'products_tbgd': products_tbgd,
        'products_ddnb': products_ddnb,
        'cart': cart,
    })

    if so_lan == 10:
        response.delete_cookie('so_lan_truy_cap')
    response.set_cookie('so_lan_truy_cap', so_lan + 1)

    return response


def danh_muc(request, pk):
    cart = Cart(request)

    # Load sản phẩm ra màn hình
    if pk == 0:     # Đọc tất cả sản phẩm
        products = Product.objects.order_by('-public_day')
        title_subcategory = f'Tất cả sản phẩm ({len(products)})'
    else:           # Đọc sản phẩm theo danh mục (subcategory)
        products = Product.objects.filter(subcategory=pk).order_by('-public_day')
        title_subcategory = f'{SubCategory.objects.get(pk=pk)} ({len(products)})'

    # Lọc giá
    range_gia = ''
    tu_khoa = ''
    if request.GET.get('gia'):
        range_gia = request.GET.get('gia')
        tu_gia, den_gia = range_gia.split('-')
        tu_khoa = request.GET.get('tu_khoa').strip()

        '''
        __lte: Less than or equal
        __gte: Greater than or equal
        __lt: Less than
        __gt: Greater than
        '''
        if pk == 0:
            
            if den_gia != '':
                products = Product.objects.filter(price__gte=tu_gia, price__lt=den_gia).order_by('-public_day')
                if tu_khoa != '':
                    products = Product.objects.filter(price__gte=tu_gia, price__lt=den_gia, name__contains=tu_khoa).order_by('-public_day')
            else:
                products = Product.objects.filter(price__gte=tu_gia).order_by('-public_day')
                if tu_khoa != '':
                    products = Product.objects.filter(price__gte=tu_gia, name__contains=tu_khoa).order_by('-public_day')
        else:
            products = Product.objects.filter(subcategory=pk, price__gte=tu_gia).order_by('-public_day')
            if den_gia != '':
                products = Product.objects.filter(subcategory=pk, price__gte=tu_gia, price__lt=den_gia).order_by('-public_day')
                if tu_khoa != '':
                    products = Product.objects.filter(subcategory=pk, price__gte=tu_gia, price__lt=den_gia, name__contains=tu_khoa).order_by('-public_day')
    
        title_subcategory = f'Tìm thấy {len(products)} sản phẩm'


    # Phân trang
    products_per_page = 9
    page = request.GET.get('trang', 1)
    paginator = Paginator(products, products_per_page)
    try:
        products_pager = paginator.page(page)
    except PageNotAnInteger:
        products_pager = paginator.page(1)
    except EmptyPage:
        products_pager = paginator.page(paginator.num_pages)

    return render(request, 'store/product-list.html', {
        'products': products,
        'products_pager': products_pager,
        'subcategories': subcategories,
        'title_subcategory': title_subcategory,
        'brands': brands,
        'cart': cart,
        'range_gia': range_gia,
        'keyword': tu_khoa,
    })


def tim_kiem(request):
    # Giỏ hàng
    cart = Cart(request)

    # Tìm kiếm
    products = []
    keyword = ''
    if request.GET.get('tu_khoa'):
        keyword = request.GET.get('tu_khoa').strip()
        products = Product.objects.filter(name__contains=keyword).order_by('-public_day')
    title_subcategory = f'Tìm thấy {len(products)} sản phẩm'

    # Lọc giá (chuyển hướng về trang danh mục)
    if request.GET.get('gia'):
        range_gia = request.GET.get('gia')
        keyword = request.GET.get('tu_khoa').strip()
        base_url = reverse('store:danh_muc', kwargs={'pk': 0})
        query_string = urlencode({'gia': range_gia, 'tu_khoa': keyword})
        url = f'{base_url}?{query_string}'
        return redirect(url)

    # Phân trang
    products_per_page = 15
    page = request.GET.get('trang', 1)
    paginator = Paginator(products, products_per_page)
    try:
        products_pager = paginator.page(page)
    except PageNotAnInteger:
        products_pager = paginator.page(1)
    except EmptyPage:
        products_pager = paginator.page(paginator.num_pages)


    return render(request, 'store/product-list.html', {
        'cart': cart,
        'brands': brands,
        'subcategories': subcategories,
        'products_pager': products_pager,
        'title_subcategory': title_subcategory,
        'keyword': keyword,
    })


def chi_tiet_san_pham(request, pk):
    # Chi tiết sản phẩm
    product = Product.objects.get(pk=pk)

    # Sản phẩm liên quan
    related_products = Product.objects.filter(subcategory=product.subcategory.pk).exclude(pk=pk).order_by('-public_day')[:20]

    # Thêm vào giỏ hàng
    quantity = 1
    if request.POST.get('btnAdd2Cart'):
        quantity = int(request.POST.get('quantity'))
        print(quantity)
        them_vao_gio_hang(request, pk, quantity)

    # Load thông tin giỏ hàng
    cart = Cart(request)

    # Hiển thị sản phẩm thường được mua kèm
    rules = pd.read_csv(os.path.join(settings.MEDIA_ROOT, 'store\\analysis\\rules.csv'), index_col=0)
    lst = rules.values.tolist()
    list_rules = []
    for item in lst:
        if str(pk) in re.findall(r'\d+[, \d+]*', item[0])[0].split(','):
            list_rules = re.findall(r'\d+[, \d+]*', item[1])[0].split(',')
    recommended_products = []
    for i in list_rules:
        recommended_products.append(Product.objects.get(pk=int(i)))

    # Thống kê số lượt xem
    product.viewed += 1
    product.save()

    return render(request, 'store/product-detail.html', {
        'cart': cart,
        'brands': brands,
        'subcategories': subcategories,
        'product': product,
        'related_products': related_products,
        'quantity': quantity,
        'recommended_products': recommended_products,
    })


def lien_he(request):
    cart = Cart(request)

    return render(request, 'store/contact.html', {
        'cart': cart,
    })


def rss(request):
    cart = Cart(request)

    newsfeed = feedparser.parse('http://feeds.feedburner.com/bedtimeshortstories/LYCF')
    entries = newsfeed.entries
    
    '''
    print(entries[0].keys())
    dict_keys(['title', 'title_detail', 'links', 'link', 'authors', 'author', 'author_detail', 
    'published', 'published_parsed', 'tags', 'id', 'guidislink', 'summary', 'summary_detail', 'content'])
    '''

    for entry in entries:
        print(entry['title'])

    return render(request, 'store/contact.html', {
        'cart': cart,
    })


# Cách 1: WebService trực tiếp
def products_service(request):
    products = Product.objects.all()
    list_products = list(products.values('name', 'price', 'image'))
    return JsonResponse(list_products, safe=False)

# Cách 2: WebService từ thư viện django rest framework
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.order_by('-public_day')
    serializer_class = ProductSerializer
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
