from gestion_usuarios.models import Usuario
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from datetime import timedelta

from gestion_usuarios.exceptions.usuarioExeptions import (
    DatosInvalidos_400, UsuarioNoEncontrado_404, ConflictoUsuario_409,
    ErrorInternoServidor_500, UsuarioNoAutorizado_401, UsuarioProhibido_403
)
from django.db.utils import IntegrityError, DatabaseError
import uuid

class UsuarioDAO:
    """
    Data Access Object (DAO) para la gestión de usuarios en la base de datos.
    Proporciona métodos para realizar operaciones CRUD sobre el modelo Usuario.
    """

    @staticmethod
    def obtener_todos():
        return Usuario.objects.filter(is_deleted=False)

    @staticmethod
    def obtener_usuario_por_id(usuario_id):
        """
        Obtiene un usuario por su ID si no ha sido eliminado.
        """
        usuario = Usuario.objects.filter(id=usuario_id, is_deleted=False).first()
        if not usuario:
            raise UsuarioNoEncontrado_404()
        return usuario

    @staticmethod
    def activar_usuario(pk):
        usuario = UsuarioDAO.obtener_usuario_por_id(pk)
        if usuario.is_active:
            raise DatosInvalidos_400('El usuario ya estaba activo')
        usuario.is_active = True
        usuario.save()
        return usuario

    @staticmethod
    def crear_usuario(data):
        """
        Crea un nuevo usuario validando que el username y email no existan previamente.
        """
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            raise DatosInvalidos_400("Faltan campos obligatorios (username, email, password)")

        if Usuario.objects.filter(username=username).exists() or Usuario.objects.filter(email=email).exists():
            raise ConflictoUsuario_409("El nombre de usuario o el correo electrónico ya se encuentran registrados.")

        try:
            # Encriptamos la contraseña antes de guardarla
            hashed_password = make_password(password)
            
            usuario = Usuario.objects.create(
                username=username,
                email=email,
                password=hashed_password,
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                role=data.get('role', 'usuario')
            )
            return usuario
        except Exception as e:
            raise ErrorInternoServidor_500(f"Error al crear el usuario: {str(e)}")

    @staticmethod
    def actualizar_usuario(pk, data):
        """
        Actualiza los datos de un usuario existente.
        """
        usuario = UsuarioDAO.obtener_usuario_por_id(pk)
        
        username = data.get('username')
        email = data.get('email')

        # Validar si el nuevo username ya está en uso por otro usuario
        if username and Usuario.objects.filter(username=username).exclude(id=pk).exists():
            raise ConflictoUsuario_409("El nombre de usuario ya está en uso.")
        
        # Validar si el nuevo email ya está en uso por otro usuario
        if email and Usuario.objects.filter(email=email).exclude(id=pk).exists():
            raise ConflictoUsuario_409("El correo electrónico ya está en uso.")

        try:
            usuario.username = username or usuario.username
            usuario.email = email or usuario.email
            usuario.first_name = data.get('first_name', usuario.first_name)
            usuario.last_name = data.get('last_name', usuario.last_name)
            usuario.role = data.get('role', usuario.role)
            usuario.save()
            return usuario
        except Exception as e:
            raise ErrorInternoServidor_500(f"Error al actualizar el usuario: {str(e)}")

    @staticmethod
    def eliminar_usuario(pk):
        """
        Realiza una eliminación lógica del usuario cambiando is_deleted a True e is_active a False.
        """
        usuario = UsuarioDAO.obtener_usuario_por_id(pk)
        if usuario.is_deleted:
            raise UsuarioNoEncontrado_404("El usuario ya se encuentra eliminado.")
        
        usuario.is_deleted = True
        usuario.is_active = False
        usuario.deleted_at = timezone.now()
        usuario.save()
        return usuario
