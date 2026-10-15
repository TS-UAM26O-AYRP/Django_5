from django.urls import path
from gestion_usuarios.views import UsuarioListCreateAPIView, UsuarioDetailUpdateDeleteAPIView

urlpatterns = [
    path('usuarios/', UsuarioListCreateAPIView.as_view(), name='usuario-list-create'),
    path('usuarios/<uuid:pk>/', UsuarioDetailUpdateDeleteAPIView.as_view(), name='usuario-detail'),
]
