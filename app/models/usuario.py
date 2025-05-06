from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.config.db import db

class Usuario(db.Model, UserMixin):
    __tablename__ = 'Usuarios'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    nombre = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    foto_perfil = db.Column(db.String(255), default='default.jpg')
    descripcion = db.Column(db.Text)
    
    # Relaciones
    recetas = db.relationship('Receta', backref='autor', lazy=True)
    me_gustas = db.relationship('MeGusta', backref='usuario', lazy=True, foreign_keys='MeGusta.ususario_id')
    
    # Relación para seguidores
    seguidores = db.relationship(
        'Seguidor',
        foreign_keys='Seguidor.usuario_id',
        backref=db.backref('seguido', lazy='joined'),
        lazy='dynamic'
    )
    
    seguidos = db.relationship(
        'Seguidor',
        foreign_keys='Seguidor.seguidor_id',
        backref=db.backref('seguidor', lazy='joined'),
        lazy='dynamic'
    )
    
    def __init__(self, nombre, email, contrasena, foto_perfil='default.jpg', descripcion=None):
        self.nombre = nombre
        self.email = email
        self.set_password(contrasena)
        self.foto_perfil = foto_perfil
        self.descripcion = descripcion

    def set_password(self, contrasena):
        self.contrasena = generate_password_hash(contrasena)
    
    def check_password(self, contrasena):
        return check_password_hash(self.contrasena, contrasena)
    
    def seguir(self, usuario):
        if not self.is_following(usuario):
            seguidor = Seguidor(usuario_id=usuario.id, seguidor_id=self.id)
            db.session.add(seguidor)
            return True
        return False
    
    def dejar_de_seguir(self, usuario):
        seguidor = Seguidor.query.filter_by(
            usuario_id=usuario.id,
            seguidor_id=self.id
        ).first()
        if seguidor:
            db.session.delete(seguidor)
            return True
        return False
    
    def is_following(self, usuario):
        return Seguidor.query.filter_by(
            usuario_id=usuario.id,
            seguidor_id=self.id
        ).first() is not None
    
    def get_seguidores(self):
        return Usuario.query.join(
            Seguidor, Seguidor.seguidor_id == Usuario.id
        ).filter(Seguidor.usuario_id == self.id).all()
    
    def get_seguidos(self):
        return Usuario.query.join(
            Seguidor, Seguidor.usuario_id == Usuario.id
        ).filter(Seguidor.seguidor_id == self.id).all()
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'foto_perfil': self.foto_perfil,
            'descripcion': self.descripcion,
            'num_recetas': len(self.recetas),
            'num_seguidores': self.seguidores.count(),
            'num_seguidos': self.seguidos.count()
        }