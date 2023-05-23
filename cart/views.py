from django.shortcuts import render, redirect, get_object_or_404
from cart.cart import Cart
from store.models import Product
from customer.models import Customer
from cart.models import Order, OrderItem
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from datetime import datetime
from django.views.decorators.http import require_POST


# Create your views here.
def gio_hang(request):
    cart = Cart(request)

    # Cập nhật giỏ hàng
    if request.POST.get('btnCapNhatGioHang'):
        cart_new = {}
        for c in cart:
            quantity_new = int(request.POST.get('quantity2' + str(c['product'].pk)))
            if quantity_new > 0:
                product_cart = {
                    str(c['product'].pk): {
                        'quantity': quantity_new, 
                        'price': str(c['price']), 
                        'coupon': str(c['coupon'])
                    }
                }
                cart_new.update(product_cart)
                c['quantity'] = quantity_new  # Giữ lại giá trị mới trong ô
            else:
                cart.remove(c['product'])
        else:
            # Chờ khi nào vòng lặp chạy xong thì sẽ update lại session cart
            request.session['cart'] = cart_new

    # print(request.session.get('cart'))

    return render(request, 'store/cart.html', {
        'cart': cart,
    })


def thanh_toan(request):
    cart = Cart(request)

    if len(cart) == 0:
        return redirect('cart:gio_hang')
    
    # Sử dụng mã giảm giá
    ds_ma_giam_gia = [
        {'TTTH': 0.8},
        {'LNT': 0.9}
    ]
    ma_giam_gia = ''
    if request.POST.get('btnMaGiamGia'):
        ma_giam_gia = request.POST.get('ma_giam_gia').strip()
        giam_gia = 1
        for dict_ma_giam_gia in ds_ma_giam_gia:
            if ma_giam_gia in dict_ma_giam_gia:
                giam_gia = dict_ma_giam_gia[ma_giam_gia]
            cart_new = {}
            for c in cart:
                print(giam_gia)
                product_cart = {
                    str(c['product'].pk): {
                        'quantity': c['quantity'], 
                        'price': str(c['price']), 
                        'coupon': str(giam_gia)
                    }
                }
                cart_new.update(product_cart)
                c['coupon'] = giam_gia  # Giữ lại giá trị coupon mới
            else:
                # Chờ khi nào vòng lặp chạy xong thì sẽ update lại session cart
                request.session['cart'] = cart_new

    # Đặt hàng => Lưu thông tin đơn hàng vào CSDL
    if request.POST.get('btnDatHang'):
        khach_hang = Customer.objects.get(pk=request.session.get('s_khachhang')['id'])
        
        # Lưu vào table Order
        order = Order()
        order.customer = khach_hang
        order.total = cart.get_final_total_price()
        order.save()

        # Lưu vào table OrderItem
        for c in cart:
            OrderItem.objects.create(order=order,
                                     product=c['product'],
                                     price=c['price'],
                                     quantity=c['quantity'],
                                     discount=c['price'] * c['quantity'] * (1 - c['coupon']),
                                     total_price=c['total_price']
                                     )

        # Gửi mail
        ngay_hien_tai = datetime.now()
        tieu_de = f"[{ngay_hien_tai.strftime('%Y%m%d%H%M%S')}] Đặt hàng thành công"
        nguoi_gui = settings.EMAIL_HOST_USER
        danh_sach_nguoi_nhan = [khach_hang.email]
        
        # Gửi thông tin plain text
        # noi_dung = 'Test mail'
        # send_mail(tieu_de, noi_dung, nguoi_gui, danh_sach_nguoi_nhan)

        # Gửi thông tin có định dạng
        noi_dung = '<p>Các mặt hàng đã đặt:</p>'
        noi_dung += '<ul>'
        for c in cart:
            noi_dung += f'<li>{c["product"]}</li>'
        noi_dung += '</ul>'

        msg = EmailMessage(tieu_de, noi_dung, nguoi_gui, danh_sach_nguoi_nhan)
        msg.content_subtype = 'html'
        msg.send()

        # Xóa tất cả các sản phẩm ra khỏi giỏ hàng
        cart.clear()

        return render(request, 'cart/result.html', {
            'cart': cart,
        })

    return render(request, 'store/checkout.html', {
        'cart': cart,
        'ma_giam_gia': ma_giam_gia,
    })


@require_POST
def mua_ngay(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    if request.POST.get('btnMuaNgay' + str(product_id)):
        quantity = int(request.POST.get('quantity' + str(product_id)))
        cart.add(product, quantity)
    return redirect('cart:gio_hang')


@require_POST
def them_vao_gio_hang(request, product_id, quantity):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product, quantity)


@require_POST
def xoa_san_pham(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:gio_hang')
