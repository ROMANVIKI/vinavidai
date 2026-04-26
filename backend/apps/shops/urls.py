# apps/shops/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("categories/", views.ShopCategoryListView.as_view(), name="shop-categories"),
    path("", views.ShopListCreateView.as_view(), name="shop-list-create"),
    path("nearby/", views.NearbyShopsView.as_view(), name="shops-nearby"),
    path("<slug:slug>/", views.ShopDetailView.as_view(), name="shop-detail"),
]
