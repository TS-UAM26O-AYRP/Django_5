# gestion_productos/serializers.py

from rest_framework import serializers
from .models import Productos

class ProductoCompletoSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    
    class Meta:
        model = Productos
        fields = [
            "id",
            "type",
            "name",
            "price",
            "status",
            "description",
            "product_key",
            "image_link",
        ]

class ProductoParcialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Productos
        fields = [
            "type",
            "name",
            "price",
            "status",
            "description",
            "product_key",
            "image_link",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hace que todos los campos sean opcionales de forma dinámica para las actualizaciones parciales
        for field in self.fields.values():
            field.required = False

