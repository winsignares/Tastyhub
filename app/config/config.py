import os
from datetime import timedelta

class Config:
    # Configuración general
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_desarrollo_cambiar_en_produccion')
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    
    # Configuración de la base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:rootpassword@localhost:3306/recetas_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de seguridad
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'sal_desarrollo_cambiar_en_produccion')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt_desarrollo_cambiar_en_produccion')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    # Configuración de uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Configuración de correo electrónico
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@recetas-app.com')