from apps.notifications.models import PriceAlert, RecentlySeen, Wishlist
from django.contrib import admin

# Register your models here.

admin.site.register(Wishlist)
admin.site.register(PriceAlert)
admin.site.register(RecentlySeen)
