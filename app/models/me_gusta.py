from app.config.db import db

class MeGusta(db.Model):
    __tablename__ = 'Me_gusta'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    ususario_id = db.Column(db.Integer, db.ForeignKey('Usuarios.id'), nullable=False)
    receta_id = db.Column(db.Integer, db.ForeignKey('Recetas.id'), nullable=False)
    
    def __init__(self, ususario_id, receta_id):
        self.ususario_id = ususario_id
        self.receta_id = receta_id