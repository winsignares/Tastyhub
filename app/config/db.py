from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Inicializar SQLAlchemy
db = SQLAlchemy()

# Inicializar Flask-Migrate
migrate = Migrate()