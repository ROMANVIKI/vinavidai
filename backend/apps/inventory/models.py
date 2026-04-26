import uuid
from django.db import models
from django.db.models import Sum
from apps.accounts.models import CustomUser
from apps.shops.models import Shop


# ── Location hierarchy ─────────────────────────────────────────────────────────


class LocationNode(models.Model):
    """
    Adjacency-list tree: up to 6 levels deep.
    L1=Floor, L2=Section, L3=Aisle, L4=Rack, L5=Shelf, L6=Bin
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shop = models.ForeignKey(
        Shop, on_delete=models.CASCADE, related_name="location_nodes", db_index=True
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    level = models.PositiveSmallIntegerField()  # 1–6
    name = models.CharField(max_length=150)  # "Ground Floor", "Aisle 3"
    code = models.CharField(max_length=50, blank=True)  # "GF", "A3"
    path = models.TextField(db_index=True)  # "Ground Floor > Men's Wear > Aisle 3"
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inventory_locationnode"
        indexes = [
            models.Index(fields=["shop", "level"]),
            models.Index(fields=["parent"]),
        ]

    def build_path(self):
        if self.parent:
            return f"{self.parent.path} > {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        self.path = self.build_path()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.path


# ── Product catalogue ──────────────────────────────────────────────────────────


class ProductCategory(models.Model):
    """Self-referential tree, scoped to a ShopCategory vertical."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    shop_category = models.ForeignKey(
        "shops.ShopCategory", on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "inventory_productcategory"
        verbose_name_plural = "product categories"

    def __str__(self):
        return self.name


class Brand(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=210, unique=True)
    logo_url = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "inventory_brand"

    def __str__(self):
        return self.name


class AttributeSchema(models.Model):
    """
    Defines which attributes are expected per shop vertical.
    e.g. Clothing → size, color, gender, fabric
         Electronics → ram_gb, storage_gb, color
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shop_category = models.ForeignKey(
        "shops.ShopCategory", on_delete=models.CASCADE, related_name="attribute_schemas"
    )
    key = models.CharField(max_length=100)  # "size", "ram_gb"
    label = models.CharField(max_length=100)  # "Size", "RAM (GB)"
    data_type = models.CharField(
        max_length=20, default="string"
    )  # string | number | boolean
    is_variant = models.BooleanField(default=False)  # True = drives ProductVariant rows
    is_filterable = models.BooleanField(default=True)  # shown in search filter panel
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "inventory_attributeschema"
        unique_together = [("shop_category", "key")]


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shop = models.ForeignKey(
        Shop, on_delete=models.CASCADE, related_name="products", db_index=True
    )
    category = models.ForeignKey(
        ProductCategory, on_delete=models.PROTECT, db_index=True
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, blank=True, db_index=True
    )

    # Core identity
    sku = models.CharField(max_length=100, blank=True)  # unique per shop
    barcode = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    name = models.CharField(max_length=350)
    description = models.TextField(blank=True)

    # Pricing
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    compare_at_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    # compare_at_price = MRP / original price — shown as strikethrough

    # Dynamic attributes — stored as JSON, validated against AttributeSchema
    # e.g. {"gender": "Men", "fabric": "Cotton", "color": "Navy"}
    attributes = models.JSONField(default=dict)

    # Stock — denormalised sum kept in sync by signals
    total_stock = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveSmallIntegerField(default=5)

    # In-store location — MVP: free-text fields
    # Post-MVP Sprint 8: replace with primary_location_node FK
    floor_label = models.CharField(max_length=100, blank=True)  # "Ground Floor"
    aisle_label = models.CharField(max_length=100, blank=True)  # "Aisle 3"
    shelf_label = models.CharField(max_length=100, blank=True)  # "Shelf 4"
    # LocationNode FK (Sprint 8 upgrade — nullable for now)
    primary_location_node = models.ForeignKey(
        LocationNode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        db_index=True,
    )
    bin_label = models.CharField(max_length=100, blank=True)  # "Bin 6", "Hook 12"
    location_notes = models.TextField(blank=True)  # "Near window display"
    location_updated_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        db_table = "inventory_product"
        unique_together = [("shop", "sku")]
        indexes = [
            models.Index(fields=["shop", "is_active"]),
            models.Index(fields=["category", "is_active", "total_stock"]),
            models.Index(fields=["base_price"]),
        ]

    def recalculate_stock(self):
        """Sync total_stock from variant stock counts."""
        total = (
            self.variants.filter(is_active=True).aggregate(s=Sum("stock_count"))["s"]
            or 0
        )
        Product.objects.filter(pk=self.pk).update(total_stock=total)

    def __str__(self):
        return f"{self.name} ({self.shop.name})"


class ProductVariant(models.Model):
    """
    One row per combination of variant attributes.
    e.g. {"size": "XL", "color": "Red"}
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    variant_attributes = models.JSONField()  # {"size": "XL", "color": "Red"}
    sku_suffix = models.CharField(max_length=50, blank=True)  # "-XL-RED"
    stock_count = models.PositiveIntegerField(default=0)
    price_override = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    # NULL = inherit parent base_price
    location_node_override = models.ForeignKey(
        LocationNode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="variant_overrides",
    )
    bin_label_override = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "inventory_productvariant"

    @property
    def effective_price(self):
        return (
            self.price_override
            if self.price_override is not None
            else self.product.base_price
        )

    def __str__(self):
        return f"{self.product.name} — {self.variant_attributes}"


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    url = models.TextField()  # Cloudflare R2 / S3 URL
    alt_text = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inventory_productimage"
        ordering = ["sort_order"]


class PriceHistory(models.Model):
    """Written by a post_save signal every time base_price changes."""

    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="price_history", db_index=True
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "inventory_pricehistory"
        ordering = ["-recorded_at"]
        get_latest_by = "recorded_at"


class StockMovement(models.Model):
    """Immutable audit log — never update, never delete."""

    class Reason(models.TextChoices):
        SALE = "sale", "Sale"
        RESTOCK = "restock", "Restock"
        ADJUSTMENT = "adjustment", "Manual Adjustment"
        IMPORT = "import", "CSV Import"
        DAMAGED = "damaged", "Damaged / Lost"
        RETURN = "return", "Customer Return"

    id = models.BigAutoField(primary_key=True)
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="movements",
        db_index=True,
    )
    change_qty = models.IntegerField()  # positive = stock in, negative = stock out
    reason = models.CharField(max_length=30, choices=Reason.choices)
    reference = models.CharField(
        max_length=200, blank=True
    )  # order ID, PO number, CSV batch ID
    performed_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "inventory_stockmovement"
        ordering = ["-created_at"]
