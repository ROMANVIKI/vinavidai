from apps.inventory.models import (
    AttributeSchema,
    Brand,
    LocationNode,
    PriceHistory,
    Product,
    ProductCategory,
    ProductImage,
    ProductVariant,
    StockMovement,
)
from django.contrib import admin

# Register your models here.
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductVariant)
admin.site.register(ProductCategory)
admin.site.register(LocationNode)
admin.site.register(AttributeSchema)
admin.site.register(PriceHistory)
admin.site.register(StockMovement)
