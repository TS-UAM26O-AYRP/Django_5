from rest_framework import serializers
from gestion_usuarios.models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'role',
            'is_active',
            'is_deleted',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'is_deleted']
