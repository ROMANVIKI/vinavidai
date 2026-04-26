from apps.shops.models import Shop, ShopCategory, ShopImage
from django.contrib import admin

# Register your models here.
admin.site.register(ShopCategory)
admin.site.register(Shop)
admin.site.register(ShopImage)
