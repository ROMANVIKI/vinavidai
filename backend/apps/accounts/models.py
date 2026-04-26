import uuid
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        SHOPPER = "shopper", "Shopper"
        OWNER = "owner", "Shop Owner"
        STAFF = "staff", "Shop Staff"
        ADMIN = "admin", "Platform Admin"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=200)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.SHOPPER)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)  # email/phone verified
    is_staff = models.BooleanField(default=False)  # Django admin access
    avatar_url = models.TextField(null=True, blank=True)
    preferred_radius_km = models.PositiveSmallIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]
    objects = CustomUserManager()

    class Meta:
        db_table = "users_customuser"

    def __str__(self):
        return f"{self.full_name} <{self.email}>"


class StaffMembership(models.Model):
    class Permission(models.TextChoices):
        VIEWER = "viewer", "Viewer"
        EDITOR = "editor", "Editor"  # can update stock/price
        MANAGER = "manager", "Manager"  # full product edit

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="memberships"
    )
    shop = models.ForeignKey(
        "shops.Shop", on_delete=models.CASCADE, related_name="staff_memberships"
    )
    permission_level = models.CharField(
        max_length=20, choices=Permission.choices, default=Permission.EDITOR
    )
    invited_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invites_sent",
    )
    joined_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "users_staffmembership"
        unique_together = [("user", "shop")]

    def __str__(self):
        return f"{self.user.email} @ {self.shop.name} ({self.permission_level})"
