
from flask import Blueprint

# Crear blueprint principal para la API
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Importar todas las rutas
from . import auth
from . import usuarios
from . import recetas
from . import categorias
from . import ingredientes
from . import seguidores