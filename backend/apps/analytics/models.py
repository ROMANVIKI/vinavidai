from django.db import models
from apps.accounts.models import CustomUser
from apps.shops.models import Shop
from apps.inventory.models import Product


class SearchEvent(models.Model):
    """Every geo-search query — written async via Celery."""

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    session_key = models.CharField(max_length=64, blank=True)  # for anonymous tracking
    query = models.CharField(max_length=500, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    radius_km = models.PositiveSmallIntegerField(null=True, blank=True)
    result_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "analytics_searchevent"


class ProductImpression(models.Model):
    """Fired when a product card appears in search results."""

    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="impressions"
    )
    search_event = models.ForeignKey(
        SearchEvent, on_delete=models.SET_NULL, null=True, blank=True
    )
    position = models.PositiveSmallIntegerField(default=0)  # rank in results
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analytics_productimpression"


class DirectionClick(models.Model):
    """Fired when user taps 'Get Directions' — footfall attribution proxy."""

    id = models.BigAutoField(primary_key=True)
    shop = models.ForeignKey(
        Shop, on_delete=models.CASCADE, related_name="direction_clicks"
    )
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "analytics_directionclick"
