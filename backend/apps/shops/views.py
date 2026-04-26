from django.shortcuts import render
from .serializers import ShopSerializer, ShopCategorySerializer
from .models import ShopCategory, Shop
from rest_framework import generics, permissions
from rest_framework.views import APIView
# Create your views here.


class ShopCategoryListView(generics.ListAPIView):
    queryset = ShopCategory.objects.filter(is_active=True)
    serializer_class = ShopCategorySerializer
    permission_classes = [permissions.AllowAny]


class ShopListCreateView(generics.ListCreateAPIView):
    queryset = Shop.objects.select_related("primary_category").prefetch_related(
        "images"
    )
    serializer_class = ShopSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ShopDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Shop.objects.select_related("primary_category").prefetch_related(
        "images"
    )
    serializer_class = ShopSerializer
    lookup_field = "slug"
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class NearbyShopsView(APIView):
    """Find shops within a radius using PostGIS"""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        radius_km = float(request.query_params.get("radius", 5))

        if not lat or not lng:
            return Response({"error": "lat and lng are required"}, status=400)

        user_location = Point(float(lng), float(lat), srid=4326)
        shops = (
            Shop.objects.filter(
                location__distance_lte=(user_location, D(km=radius_km)),
                status=Shop.Status.ACTIVE,
            )
            .select_related("primary_category")
            .prefetch_related("images")
        )

        serializer = ShopListSerializer(shops, many=True)
        return Response(serializer.data)
