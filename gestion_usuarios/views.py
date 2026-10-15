from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from gestion_usuarios.DAO.usuarioDAO import UsuarioDAO
from gestion_usuarios.serializers import UsuarioSerializer
from gestion_usuarios.exceptions.usuarioExeptions import (
    DatosInvalidos_400,
    UsuarioNoEncontrado_404,
    ConflictoUsuario_409,
    ErrorInternoServidor_500
)

class UsuarioListCreateAPIView(APIView):
    """
    Endpoints para listar y crear usuarios.
    """
    def get(self, request):
        """Obtener la lista de todos los usuarios."""
        try:
            usuarios = UsuarioDAO.obtener_todos()
            serializer = UsuarioSerializer(usuarios, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        request_body=UsuarioSerializer,
        responses={201: UsuarioSerializer(), 400: "Datos inválidos", 409: "Conflicto"}
    )
    def post(self, request):
        """Crear un nuevo usuario."""
        try:
            usuario = UsuarioDAO.crear_usuario(request.data)
            serializer = UsuarioSerializer(usuario)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except DatosInvalidos_400 as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ConflictoUsuario_409 as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except ErrorInternoServidor_500 as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": f"Error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UsuarioDetailUpdateDeleteAPIView(APIView):
    """
    Endpoints para obtener, actualizar y eliminar un usuario específico por ID.
    """
    def get(self, request, pk):
        """Obtener un usuario por su ID."""
        try:
            usuario = UsuarioDAO.obtener_usuario_por_id(pk)
            serializer = UsuarioSerializer(usuario)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UsuarioNoEncontrado_404 as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        request_body=UsuarioSerializer,
        responses={200: UsuarioSerializer(), 400: "Datos inválidos", 404: "No encontrado", 409: "Conflicto"}
    )
    def put(self, request, pk):
        """Actualizar un usuario existente."""
        try:
            usuario = UsuarioDAO.actualizar_usuario(pk, request.data)
            serializer = UsuarioSerializer(usuario)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UsuarioNoEncontrado_404 as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except DatosInvalidos_400 as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ConflictoUsuario_409 as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except ErrorInternoServidor_500 as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        """Eliminación lógica de un usuario."""
        try:
            UsuarioDAO.eliminar_usuario(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UsuarioNoEncontrado_404 as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
