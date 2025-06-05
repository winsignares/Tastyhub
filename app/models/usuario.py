from flask_login import UserMixin
from app.config.db import db
from datetime import datetime

class Usuario(UserMixin, db.Model):
    __tablename__ = 'Usuarios'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    foto_perfil = db.Column(db.String(255), default='default.jpg')
    descripcion = db.Column(db.Text)
    
    # Relaciones
    recetas = db.relationship('Receta', backref='autor', lazy=True, cascade='all, delete-orphan')
    me_gustas = db.relationship('MeGusta', backref='usuario', lazy=True, cascade='all, delete-orphan', foreign_keys='MeGusta.ususario_id')
    
    # Relación para seguidores usando tu estructura existente
    seguidores = db.relationship(
        'Seguidor',
        foreign_keys='Seguidor.usuario_id',
        backref=db.backref('seguido', lazy='joined'),
        lazy='dynamic'
    )
    
    seguidos = db.relationship(
        'Seguidor',
        foreign_keys='Seguidor.seguidor_id',
        backref=db.backref('seguidor_usuario', lazy='joined'),
        lazy='dynamic'
    )
    
    def __init__(self, nombre, email, contrasena, foto_perfil='default.jpg', descripcion=None):
        self.nombre = nombre
        self.email = email
        self.set_password(contrasena)
        self.foto_perfil = foto_perfil
        self.descripcion = descripcion

    def set_password(self, contrasena):
        from werkzeug.security import generate_password_hash
        self.contrasena = generate_password_hash(contrasena)
    
    def check_password(self, contrasena):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.contrasena, contrasena)
    
    def get_id(self):
        """Método requerido por Flask-Login"""
        return str(self.id)
    
    def seguir(self, usuario):
        """Seguir a otro usuario"""
        if not self.is_following(usuario):
            from app.models.seguidor import Seguidor
            seguidor = Seguidor(usuario_id=usuario.id, seguidor_id=self.id)
            db.session.add(seguidor)
            return True
        return False
    
    def dejar_de_seguir(self, usuario):
        """Dejar de seguir a un usuario"""
        from app.models.seguidor import Seguidor
        seguidor = Seguidor.query.filter_by(
            usuario_id=usuario.id,
            seguidor_id=self.id
        ).first()
        if seguidor:
            db.session.delete(seguidor)
            return True
        return False
    
    def is_following(self, usuario):
        """Verificar si sigue a un usuario"""
        from app.models.seguidor import Seguidor
        return Seguidor.query.filter_by(
            usuario_id=usuario.id,
            seguidor_id=self.id
        ).first() is not None
    
    def get_seguidores(self):
        """Obtener lista de seguidores"""
        from app.models.seguidor import Seguidor
        return Usuario.query.join(
            Seguidor, Usuario.id == Seguidor.seguidor_id
        ).filter(Seguidor.usuario_id == self.id).all()
    
    def get_seguidos(self):
        """Obtener lista de usuarios que sigue"""
        from app.models.seguidor import Seguidor
        return Usuario.query.join(
            Seguidor, Usuario.id == Seguidor.usuario_id
        ).filter(Seguidor.seguidor_id == self.id).all()
    
    def contar_seguidores(self):
        """Contar número de seguidores"""
        from app.models.seguidor import Seguidor
        return Seguidor.query.filter_by(usuario_id=self.id).count()
    
    def contar_seguidos(self):
        """Contar número de usuarios que sigue"""
        from app.models.seguidor import Seguidor
        return Seguidor.query.filter_by(seguidor_id=self.id).count()
    
    def to_dict(self):
        """Convertir a diccionario para API"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'foto_perfil': self.foto_perfil,
            'descripcion': self.descripcion,
            'num_recetas': len(self.recetas),
            'num_seguidores': self.contar_seguidores(),
            'num_seguidos': self.contar_seguidos()
        }