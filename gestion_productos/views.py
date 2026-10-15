from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .DAO.productoDAO import ProductoDAO
from gestion_productos.serializers import ProductoCompletoSerializer, ProductoParcialSerializer
from gestion_productos.exceptions.productoExceptions import (
    DatosInvalidos_400,
    ProductoNoEncontrado_404,
    ConflictoProducto_409,
    ErrorInternoServidor_500,
    ProductoNoAutorizado_401,
    ProductoProhibido_403,
)

class ProductoViewSet(viewsets.ViewSet):
    """
    API para la gestión de Productos.
    """

    @swagger_auto_schema(
        operation_summary="Obtener todos los productos",
        responses={200: ProductoCompletoSerializer(many=True), 500: "Error interno"}
    )
    def list(self, request, *args, **kwargs):
        try:
            productos = ProductoDAO.obtener_todos()
            serializer = ProductoCompletoSerializer(productos, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Obtener un producto por ID",
        responses={200: ProductoCompletoSerializer(), 404: "No encontrado"}
    )
    def retrieve(self, request, pk=None):
        try:
            producto = ProductoDAO.obtener_producto_por_id(pk)
            serializer = ProductoCompletoSerializer(producto)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ProductoNoEncontrado_404 as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Crear un nuevo producto",
        request_body=ProductoCompletoSerializer,
        responses={201: ProductoCompletoSerializer(), 400: "Validación errónea", 409: "Conflicto"}
    )
    def create(self, request):
        try:
            producto = ProductoDAO.crear_producto(**request.data)
            return Response(ProductoCompletoSerializer(producto).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": e.detail if hasattr(e, 'detail') else str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ConflictoProducto_409 as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Actualizar un producto (completo)",
        request_body=ProductoCompletoSerializer,
        responses={200: ProductoCompletoSerializer(), 404: "No encontrado"}
    )
    def update(self, request, pk=None):
        try:
            producto = ProductoDAO.actualizar_producto(pk, **request.data)
            return Response(ProductoCompletoSerializer(producto).data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": e.detail if hasattr(e, 'detail') else str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ProductoNoEncontrado_404 as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Actualizar un producto (parcialmente)",
        request_body=ProductoParcialSerializer,
        responses={200: ProductoParcialSerializer(), 404: "No encontrado"}
    )
    def partial_update(self, request, pk=None):
        try:
            producto = ProductoDAO.actualizar_producto_parcial(pk, **request.data)
            return Response(ProductoParcialSerializer(producto).data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": e.detail if hasattr(e, 'detail') else str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ProductoNoEncontrado_404 as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Elimina un producto (borrado lógico).",
        responses={200: "Eliminado correctamente", 404: "No encontrado"}
    )
    def destroy(self, request, pk=None):
        try:
            ProductoDAO.eliminar_producto(pk)
            return Response({"mensaje": "Producto eliminado correctamente"}, status=status.HTTP_200_OK)
        except ProductoNoEncontrado_404 as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"])
    @swagger_auto_schema(
        operation_summary="Restaurar un producto eliminado.",
        responses={200: "Restaurado exitosamente", 404: "No encontrado"}
    )
    def restore(self, request, pk=None):
        try:
            ProductoDAO.restaurar_producto(pk)
            return Response({"mensaje": "Producto restaurado correctamente"}, status=status.HTTP_200_OK)
        except ProductoNoEncontrado_404 as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], url_path="search")
    @swagger_auto_schema(
        operation_summary="Buscar productos por nombre o descripción",
        manual_parameters=[
            openapi.Parameter('q', openapi.IN_QUERY, description="Texto a buscar", type=openapi.TYPE_STRING, required=True)
        ],
        responses={200: ProductoCompletoSerializer(many=True)}
    )
    def search(self, request):
        query = request.GET.get("q", "")
        if not query:
            return Response({"error": "Debe proporcionar un parámetro de búsqueda"}, status=status.HTTP_400_BAD_REQUEST)
        productos = ProductoDAO.buscar_productos(query)
        serializer = ProductoCompletoSerializer(productos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="filtrar-precio")
    @swagger_auto_schema(
        operation_summary="Filtrar productos por rango de precio",
        manual_parameters=[
            openapi.Parameter('precio_min', openapi.IN_QUERY, description="Precio mínimo", type=openapi.TYPE_NUMBER, required=True),
            openapi.Parameter('precio_max', openapi.IN_QUERY, description="Precio máximo", type=openapi.TYPE_NUMBER, required=True),
        ],
        responses={200: "Éxito"}
    )
    def filtrar_por_precio(self, request):
        try:
            precio_min = request.query_params.get("precio_min")
            precio_max = request.query_params.get("precio_max")
            if precio_min is None or precio_max is None:
                return Response({"error": "Debe proporcionar precio_min y precio_max"}, status=status.HTTP_400_BAD_REQUEST)
            productos = ProductoDAO.filtrar_por_rango_precio(precio_min, precio_max)
            serializer = ProductoCompletoSerializer(productos, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["patch"])
    @swagger_auto_schema(
        operation_summary="Actualizar imagen de producto",
        manual_parameters=[
            openapi.Parameter('image_link', openapi.IN_QUERY, description="URL válida", type=openapi.TYPE_STRING, required=True)
        ],
        responses={200: "Imagen actualizada"}
    )
    def update_image(self, request, pk=None):
        try:
            img = request.GET.get("image_link", "")
            producto = ProductoDAO.actualizar_img(pk, img)
            return Response({
                "codigo": 200,
                "mensaje": "Imagen del producto actualizada exitosamente.",
                "resultado": {
                    "id": str(producto.id),
                    "image_link": producto.image_link,
                    "modified_at": producto.modified_at.isoformat()
                }
            }, status=status.HTTP_200_OK)
        except ProductoNoEncontrado_404 as e:
            return Response({"codigo": 404, "mensaje": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"codigo": 400, "mensaje": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"codigo": 500, "mensaje": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["patch"])
    @swagger_auto_schema(
        operation_summary="Desactivar un producto",
        responses={200: "Desactivado exitosamente"}
    )
    def deactivate(self, request, pk=None):
        try:
            producto = ProductoDAO.desactivar_producto(pk)
            return Response({
                "codigo": 200,
                "mensaje": "Producto desactivado exitosamente.",
                "resultado": {
                    "id": str(producto.id),
                    "status": producto.status,
                    "modified_at": producto.modified_at.isoformat()
                }
            }, status=status.HTTP_200_OK)
        except ProductoNoEncontrado_404 as e:
            return Response({"codigo": 404, "mensaje": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"codigo": 400, "mensaje": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"codigo": 500, "mensaje": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["patch"])
    @swagger_auto_schema(
        operation_summary="Activar un producto",
        responses={200: "Activado correctamente"}
    )
    def activate(self, request, pk=None):
        try:
            ProductoDAO.activar_producto(pk)
            return Response({"mensaje": "Producto activado correctamente"}, status=status.HTTP_200_OK)
        except ProductoNoEncontrado_404 as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
