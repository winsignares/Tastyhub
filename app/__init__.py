from flask import Flask, Blueprint, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
import os

def create_app(config_class=None):
    app = Flask(__name__, 
                template_folder='config/templates',
                static_folder='static')
    
    # Importar config aquí para evitar importaciones circulares
    from app.config.config import Config
    
    if config_class is None:
        config_class = Config
        
    app.config.from_object(config_class)
    
    # Importar db y mail aquí para evitar importaciones circulares
    from app.config.db import db
    from app.utils.email import mail
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Inicializar Flask-Migrate
    migrate = Migrate(app, db)
    
    # Inicializar Flask-Mail
    mail.init_app(app)
    
    # Inicializar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'api.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        # Importar Usuario aquí para evitar importaciones circulares
        from app.models.usuario import Usuario
        return Usuario.query.get(int(user_id))
    
    # Registrar blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp)
    
    # Crear blueprint principal
    main_bp = Blueprint('main', __name__)
    
    @main_bp.route('/')
    def index():
        # Importar modelos aquí para evitar importaciones circulares
        from app.models.receta import Receta
        from app.models.categoria import Categoria
        
        # Obtener recetas recientes
        recetas_recientes = Receta.query.order_by(Receta.fecha_creacion.desc()).limit(6).all()
        
        # Obtener categorías
        categorias = Categoria.query.all()
        
        return render_template('home-page.html', recetas_recientes=recetas_recientes, categorias=categorias)
    
    app.register_blueprint(main_bp)
    
    # Asegurarse de que existan las carpetas para uploads
    with app.app_context():
        os.makedirs(os.path.join(app.static_folder, 'uploads', 'perfiles'), exist_ok=True)
        os.makedirs(os.path.join(app.static_folder, 'uploads', 'recetas'), exist_ok=True)
    
    return app