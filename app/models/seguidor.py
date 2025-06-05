from app.config.db import db

class Seguidor(db.Model):
    __tablename__ = 'seguidores'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('Usuarios.id'), nullable=False)
    seguidor_id = db.Column(db.Integer, db.ForeignKey('Usuarios.id'), nullable=False)
    
    def __repr__(self):
        return f'<Seguidor {self.seguidor_id} -> {self.usuario_id}>'