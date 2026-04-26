from apps.analytics.models import DirectionClick, ProductImpression, SearchEvent
from django.contrib import admin

# Register your models here.


admin.site.register(SearchEvent)
admin.site.register(ProductImpression)
admin.site.register(DirectionClick)
