from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product, ProductVariant, PriceHistory


@receiver(post_save, sender=Product)
def record_price_history(sender, instance, created, **kwargs):
    """Record price every time base_price changes."""
    if created:
        PriceHistory.objects.create(product=instance, price=instance.base_price)
        return
    # Compare against latest history entry
    latest = instance.price_history.first()
    if latest is None or latest.price != instance.base_price:
        PriceHistory.objects.create(product=instance, price=instance.base_price)


@receiver(post_save, sender=ProductVariant)
def sync_total_stock(sender, instance, **kwargs):
    """Keep Product.total_stock in sync after every variant save."""
    instance.product.recalculate_stock()
