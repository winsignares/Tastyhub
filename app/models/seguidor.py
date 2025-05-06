from app.config.db import db

class Seguidor(db.Model):
    __tablename__ = 'seguidores'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('Usuarios.id'), nullable=False)
    seguidor_id = db.Column(db.Integer, db.ForeignKey('Usuarios.id'), nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'seguidor_id', name='uq_usuario_seguidor'),
    )
    
    def __init__(self, usuario_id, seguidor_id):
        self.usuario_id = usuario_id
        self.seguidor_id = seguidor_id