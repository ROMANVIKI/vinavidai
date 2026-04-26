import uuid
from django.db import models
from apps.accounts.models import CustomUser
from apps.inventory.models import Product


class Wishlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="wishlist"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="wishlisted_by"
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "shopper_wishlist"
        unique_together = [("user", "product")]


class PriceAlert(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="price_alerts"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="price_alerts"
    )
    target_price = models.DecimalField(max_digits=12, decimal_places=2)
    triggered_at = models.DateTimeField(null=True, blank=True)  # set when alert fires
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "shopper_pricealert"


class RecentlySeen(models.Model):
    """Rolling window — keep only the latest 20 per user (cleaned by Celery Beat)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="recently_seen"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="seen_by"
    )
    seen_at = models.DateTimeField(auto_now=True)  # updated on every view

    class Meta:
        db_table = "shopper_recentlyseen"
        unique_together = [("user", "product")]
        ordering = ["-seen_at"]
