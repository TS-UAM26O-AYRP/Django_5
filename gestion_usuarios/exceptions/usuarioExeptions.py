class DatosInvalidos_400(Exception):
    """Excepción para solicitudes con datos inválidos (Código 400)."""
    pass

class UsuarioNoEncontrado_404(Exception):
    """Excepción para cuando no se encuentra un usuario (Código 404)."""
    pass

class ConflictoUsuario_409(Exception):
    """Excepción para conflictos como username o email duplicados (Código 409)."""
    pass

class ErrorInternoServidor_500(Exception):
    """Excepción para errores internos inesperados del servidor (Código 500)."""
    pass

class UsuarioNoAutorizado_401(Exception):
    """Excepción para accesos no autenticados (Código 401)."""
    pass

class UsuarioProhibido_403(Exception):
    """Excepción para accesos sin permisos suficientes (Código 403)."""
    pass
