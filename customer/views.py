from django.shortcuts import render, redirect
from customer.forms import *
from customer.models import *
from django.contrib.auth.hashers import PBKDF2PasswordHasher, Argon2PasswordHasher, BCryptPasswordHasher
from cart.cart import Cart
from cart.models import Order, OrderItem
from store.models import Product
from django.conf import settings
from django.template.loader import render_to_string
from customer.libs import *
import base64
import pdfkit


salt = '123'


# Create your views here.
def dang_nhap(request):
    cart = Cart(request)

    if 's_khachhang' in request.session:
        return redirect('store:trang_chu')

    # Đăng ký
    # Lấy thông tin tỉnh/tp, quận/huyện, phường/xã
    du_lieu = read_json_internet('http://api.laptrinhpython.net/vietnam')

    # Tỉnh/TP
    list_provinces = []
    str_districts = []
    str_wards = []
    list_districts_2 = []
    for province in du_lieu:
        list_provinces.append(province['name'])
        # Quận/Huyện
        list_districts_1 = []
        for dictrict in province['districts']:
            d = dictrict['prefix'] + ' ' + dictrict['name']
            list_districts_1.append(d)
            list_districts_2.append(d)
            # Phường/Xã
            list_wards = []
            for ward in dictrict['wards']:
                w = ward['prefix'] + ' ' + ward['name']
                list_wards.append(w)
            else:
                str_wards.append('|'.join(list_wards))
        else:
            str_districts.append('|'.join(list_districts_1))

    ket_qua_dang_ky = ''
    form = FormDangKy()
    if request.POST.get('btnDangKy'):
        form = FormDangKy(request.POST, Customer)
        if form.is_valid():
            if form.cleaned_data['password'] == form.cleaned_data['confirm_password']:
                hasher = PBKDF2PasswordHasher()
                request.POST._mutable = True
                post = form.save(commit=False)
                post.first_name = form.cleaned_data['first_name']
                post.last_name = form.cleaned_data['last_name']
                post.email = form.cleaned_data['email']
                # post.password = form.cleaned_data['password']
                post.password = hasher.encode(form.cleaned_data['password'], salt)
                post.phone = form.cleaned_data['phone']
                post.address = form.cleaned_data['address'] + ', ' + form.cleaned_data['ward'] + ', ' + form.cleaned_data['district'] + ', ' + form.cleaned_data['province']
                post.save()

                ket_qua_dang_ky = '''
                <div class="alert alert-success" role="alert">
                    Đăng ký thành viên thành công
                </div>
                '''
            else:
                ket_qua_dang_ky = '''
                <div class="alert alert-danger" role="alert">
                    <b>Mật khẩu</b> và <b>Xác nhận mật khẩu</b> không khớp
                </div>
                '''
        else:
            ket_qua_dang_ky = '''
            <div class="alert alert-danger" role="alert">
                Đăng ký không thành công. Vui lòng kiểm tra lại thông tin nhập
            </div>
            '''

    # Đăng nhập
    ket_qua_dang_nhap = ''
    if request.POST.get('btnDangNhap'):
        # Gán biến
        hasher = PBKDF2PasswordHasher()
        email = request.POST.get('email')
        mat_khau = hasher.encode(request.POST.get('mat_khau'), salt)

        # SELECT * FROM customer_customer WHERE email='' AND password=''
        khach_hang = Customer.objects.filter(email=email, password=mat_khau)  
        if khach_hang.count() > 0:
            dict_khach_hang = khach_hang.values()[0]  # Chuyển QuerySet về thành dictionary
            request.session['s_khachhang'] = dict_khach_hang  # Tạo session
            return redirect('store:trang_chu')
        else:
            ket_qua_dang_nhap = '''
            <div class="alert alert-danger" role="alert">
                Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin
            </div>
            '''

    return render(request, 'store/login.html', {
        'form': form,
        'ket_qua_dang_ky': ket_qua_dang_ky,
        'ket_qua_dang_nhap': ket_qua_dang_nhap,
        'cart': cart,
        'provinces': tuple(list_provinces),
        'str_districts': tuple(str_districts),
        'str_wards': tuple(str_wards),
        'list_districts': list_districts_2,
    })


def dang_xuat(request):
    # if request.session.get('s_khachhang'):
    if 's_khachhang' in request.session:
        del request.session['s_khachhang']
    return redirect('customer:dang_nhap')


def tai_khoan_cua_toi(request):
    cart = Cart(request)

    if 's_khachhang' not in request.session:
        return redirect('customer:dang_nhap')
    
    # ====== Cập nhật thông tin tài khoản của tôi
    # Đọc thông tin người dùng đăng nhập
    ket_qua_cap_nhat = ''
    dict_khach_hang = request.session.get('s_khachhang')
    khach_hang = Customer.objects.get(pk=dict_khach_hang['id'])
    if request.POST.get('btnCapNhat'):
        # Gán biến
        ho = request.POST.get('ho')
        ten = request.POST.get('ten')
        dien_thoai = request.POST.get('dien_thoai')
        dia_chi = request.POST.get('dia_chi')

        # Cập nhật vào CSDL
        khach_hang.last_name = ho
        khach_hang.first_name = ten
        khach_hang.phone = dien_thoai
        khach_hang.address = dia_chi
        khach_hang.save()

        # Cập nhật vào session
        dict_khach_hang['last_name'] = ho
        dict_khach_hang['first_name'] = ten
        dict_khach_hang['phone'] = dien_thoai
        dict_khach_hang['address'] = dia_chi
        request.session['s_khachhang'] = dict_khach_hang

        # Kết xuất
        ket_qua_cap_nhat = '''
            <div class="alert alert-success" role="alert">
                Cập nhật thông tin thành công
            </div>
            '''
        
    # ====== Đổi mật khẩu
    ket_qua_doi_mat_khau = ''
    if request.POST.get('btnDoiMatKhau'):
        # Gán biến
        hasher = PBKDF2PasswordHasher()
        mat_khau_hien_tai = hasher.encode(request.POST.get('mat_khau_hien_tai'), salt)
        mat_khau_moi = hasher.encode(request.POST.get('mat_khau_moi'), salt)
        xac_nhan_mat_khau = hasher.encode(request.POST.get('xac_nhan_mat_khau'), salt)

        if mat_khau_hien_tai == khach_hang.password:
            if mat_khau_moi == xac_nhan_mat_khau:
                khach_hang.password = mat_khau_moi
                khach_hang.save()
                ket_qua_doi_mat_khau = '''
                    <div class="alert alert-success" role="alert">
                        Đổi mật khẩu thành công
                    </div>
                    '''
            else:
                ket_qua_doi_mat_khau = '''
                    <div class="alert alert-danger" role="alert">
                        Mật khẩu và Xác nhận mật khẩu không khớp
                    </div>
                    '''
        else:
            ket_qua_doi_mat_khau = '''
                <div class="alert alert-danger" role="alert">
                    Mật khẩu hiện tại không đúng. Vui lòng kiểm tra lại
                </div>
                '''

    # ====== Hiển thị danh sách đơn hàng
    orders = Order.objects.filter(customer=request.session['s_khachhang']['id'])
    dict_orders = {}
    for order in orders:
        order_items = list(OrderItem.objects.filter(order=order.pk).values())
        for order_item in order_items:
            product = Product.objects.get(pk=order_item['product_id'])
            order_item['product_name'] = product.name
            order_item['product_image'] = product.image
            order_item['total'] = order.total
        else:
            dict_order_items = {
                order.pk: order_items
            }
            dict_orders.update(dict_order_items)

    return render(request, 'store/my-account.html', {
        'cart': cart,
        'khach_hang': khach_hang,
        'ket_qua_cap_nhat': ket_qua_cap_nhat,
        'ket_qua_doi_mat_khau': ket_qua_doi_mat_khau,
        'orders': orders,
        'dict_orders': dict_orders,
    })


def xuat_bao_cao_don_hang(request, pk):
    if 's_khachhang' not in request.session:
        return redirect('store:trang_chu')

    khach_hang = request.session.get('s_khachhang')
    order = Order.objects.get(pk=pk, customer=khach_hang['id'])
    order_items = list(OrderItem.objects.filter(order=pk).values())
    for order_item in order_items:
        product = Product.objects.get(pk=order_item['product_id'])
        order_item['product_name'] = product.name
        with open(settings.MEDIA_ROOT + str(product.image), 'rb') as img_file:
            image_string = base64.b64encode(img_file.read())
        order_item['product_image'] = image_string.decode('utf-8')
        order_item['total'] = order.total

    # response = render(request, 'customer/report_order.html', {
    response = render_to_string('customer/report_order.html', {
        'order_date': order.created.strftime('%d-%m-%Y %H:%M:%S'),
        'order_items': order_items,
        'customer': khach_hang,
        'pk': pk,
    })

    # Xuất ra pdf
    config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
    filename = 'DH' + str(order.pk) + '.pdf'
    folder_reports = settings.MEDIA_ROOT + 'store/reports/'
    path_to_report = folder_reports + filename
    pdfkit.from_string(response, path_to_report, configuration=config)
    return redirect('/media/store/reports/' + filename)

