from django.shortcuts import render
from .serializers import CustomUserSerializer
from rest_framework import generics, permissions, filters
from .models import CustomUser

# Create your views here.


class CustomUserListView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    lookup_field = "id"
    permission_classes = [permissions.AllowAny]
