import re
from flask import current_app

def allowed_file(filename):
    """
    Verifica si el archivo tiene una extensión permitida
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def validate_email(email):
    """
    Valida el formato de un correo electrónico
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """
    Valida que la contraseña cumpla con requisitos mínimos:
    - Al menos 8 caracteres
    - Al menos una letra mayúscula
    - Al menos una letra minúscula
    - Al menos un número
    """
    import re
    if len(password) < 8:
        return False
    
    if not re.search(r'[A-Z]', password):
        return False
    
    if not re.search(r'[a-z]', password):
        return False
    
    if not re.search(r'[0-9]', password):
        return False
    
    return True

def sanitize_input(text):
    """
    Limpia texto de entrada para prevenir XSS
    """
    if text is None:
        return None
    
    # Eliminar etiquetas HTML
    text = re.sub(r'<[^>]*>', '', text)
    
    # Convertir caracteres especiales
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    
    return text