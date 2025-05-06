from app.config.db import db

class Instruccion(db.Model):
    __tablename__ = 'Instrucciones'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    id_receta = db.Column(db.Integer, db.ForeignKey('Recetas.id'), nullable=False)
    numero_paso = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    
    def __init__(self, id_receta, numero_paso, descripcion):
        self.id_receta = id_receta
        self.numero_paso = numero_paso
        self.descripcion = descripcion