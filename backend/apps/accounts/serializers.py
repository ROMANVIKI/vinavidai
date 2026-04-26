from rest_framework import serializers
from django.contrib.gis.geos import Point
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"
