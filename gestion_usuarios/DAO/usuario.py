@staticmethod
def obtener_todos():
    return Usuario.objects.all()
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
