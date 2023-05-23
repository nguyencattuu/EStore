from django.contrib import admin
from store.models import Product
from datetime import datetime
from django.utils.html import format_html


# Register your models here.
def change_public_day(modeladmin, request, queryset):
    queryset.update(public_day=datetime.now())

change_public_day.short_description = 'Change "public_day" to today'

class ProductAdmin(admin.ModelAdmin):
    exclude = ('public_day', 'viewed')
    # list_display = ('name', 'price', 'public_day', 'viewed', 'subcategory')
    list_display = ('e_name', 'e_price', 'e_public_day', 'e_viewed', 'e_subcategory', 'e_category', 'e_image')
    list_filter = ('public_day',)
    search_fields = ('name__contains',)
    actions = [change_public_day]


    @admin.display(description="Tên sản phẩm")
    def e_name(self, obj):
        return f'{obj.name}'
    
    @admin.display(description="Đơn giá")
    def e_price(self, obj):
        return '{:,}'.format(int(obj.price))
    
    @admin.display(description="Ngày đăng")
    def e_public_day(self, obj):
        return f'{obj.public_day.strftime("%d/%m/%Y %H-%M-%S")}'
    
    @admin.display(description="Số lượt xem")
    def e_viewed(self, obj):
        return f'{obj.viewed}'
    
    @admin.display(description="Danh mục")
    def e_subcategory(self, obj):
        return f'{obj.subcategory}'
    
    @admin.display(description="Danh mục cha")
    def e_category(self, obj):
        return f'{obj.subcategory.category}'
    
    @admin.display(description="Hình ảnh")
    def e_image(self, obj):
        return format_html(f'<img src="{obj.image.url}" style="width: 45px; height: 45px;" />')


admin.site.register(Product, ProductAdmin)
admin.site.site_header = 'EStore Admin'
