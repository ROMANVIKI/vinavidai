import uuid
from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.indexes import GistIndex
from django.db import models
from django.utils.text import slugify
from apps.accounts.models import CustomUser


class ShopCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon_url = models.TextField(null=True, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "shops_shopcategory"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class Shop(gis_models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending Review"
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    owner = models.ForeignKey(
        CustomUser, on_delete=models.PROTECT, related_name="owned_shops"
    )

    primary_category = models.ForeignKey(
        ShopCategory, on_delete=models.PROTECT, related_name="shops"
    )

    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    description = models.TextField(null=True, blank=True)

    address_line = models.TextField()
    city = models.CharField(max_length=100, db_index=True)

    # 🌍 Geo field (PostGIS)
    location = gis_models.PointField(srid=4326)

    google_place_id = models.CharField(
        max_length=300, null=True, blank=True, db_index=True
    )

    opening_hours = models.JSONField(null=True, blank=True)

    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    is_verified = models.BooleanField(default=False)

    # ⭐ Optional but useful
    rating = models.FloatField(default=0)
    total_reviews = models.PositiveIntegerField(default=0)

    floor_plan_url = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "shops_shop"
        indexes = [
            GistIndex(fields=["location"]),  # 🚀 critical for geo queries
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Shop.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    # ✅ Helper properties for frontend
    @property
    def latitude(self):
        return self.location.y

    @property
    def longitude(self):
        return self.location.x


class ShopImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="images")

    url = models.TextField()
    alt_text = models.CharField(max_length=200, blank=True)

    is_cover = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "shops_shopimage"
        ordering = ["sort_order"]

    def __str__(self):
        return f"Image for {self.shop.name}"
