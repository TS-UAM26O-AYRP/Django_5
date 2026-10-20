# autentificacion/urls.py

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Ruta para obtener el token de acceso y de renovación mediante credenciales
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Ruta para refrescar el token de acceso usando un token de renovación válido
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]



