from app.config.db import db

class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    nombre = db.Column(db.String(255), nullable=False, unique=True)
    descripcion = db.Column(db.Text)
    
    def __init__(self, nombre, descripcion=None):
        self.nombre = nombre
        self.descripcion = descripcion
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion
        }

class RecetaCategoria(db.Model):
    __tablename__ = 'Receta_categorias'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    receta_id = db.Column(db.Integer, db.ForeignKey('Recetas.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    
    def __init__(self, receta_id, categoria_id):
        self.receta_id = receta_id
        self.categoria_id = categoria_id