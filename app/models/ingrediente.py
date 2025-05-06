from app.config.db import db

class Ingrediente(db.Model):
    __tablename__ = 'Ingredientes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    nombre = db.Column(db.String(255), nullable=False)
    unidad_medida = db.Column(db.String(255))
    
    def __init__(self, nombre, unidad_medida=None):
        self.nombre = nombre
        self.unidad_medida = unidad_medida
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'unidad_medida': self.unidad_medida
        }

class RecetaIngrediente(db.Model):
    __tablename__ = 'Receta_ingredientes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    receta_id = db.Column(db.Integer, db.ForeignKey('Recetas.id'), nullable=False)
    ingredientes_id = db.Column(db.Integer, db.ForeignKey('Ingredientes.id'), nullable=False)
    cantidad = db.Column(db.Integer)
    
    # Relación con Ingrediente
    ingrediente = db.relationship('Ingrediente', backref='recetas_ingredientes')
    
    def __init__(self, receta_id, ingredientes_id, cantidad=None):
        self.receta_id = receta_id
        self.ingredientes_id = ingredientes_id
        self.cantidad = cantidad