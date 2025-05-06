from datetime import datetime
from app.config.db import db

class Receta(db.Model):
    __tablename__ = 'Recetas'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('Usuarios.id'), nullable=False)
    titulo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    imagen_portada = db.Column(db.String(255))
    tiempor_pre = db.Column(db.String(255))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    instrucciones = db.relationship('Instruccion', backref='receta', lazy=True, cascade='all, delete-orphan')
    me_gustas = db.relationship('MeGusta', backref='receta', lazy=True, cascade='all, delete-orphan')
    
    # Relaciones muchos a muchos
    categorias = db.relationship('Categoria', secondary='Receta_categorias', backref=db.backref('recetas', lazy='dynamic'))
    ingredientes = db.relationship('RecetaIngrediente', backref='receta', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, id_usuario, titulo, descripcion=None, imagen_portada=None, tiempor_pre=None):
        self.id_usuario = id_usuario
        self.titulo = titulo
        self.descripcion = descripcion
        self.imagen_portada = imagen_portada
        self.tiempor_pre = tiempor_pre
        self.fecha_creacion = datetime.utcnow()
    
    def contar_me_gustas(self):
        return len(self.me_gustas)
    
    def usuario_dio_me_gusta(self, usuario_id):
        return any(mg.ususario_id == usuario_id for mg in self.me_gustas)
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_usuario': self.id_usuario,
            'autor': self.autor.nombre,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'imagen_portada': self.imagen_portada,
            'tiempor_pre': self.tiempor_pre,
            'fecha_creacion': self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
            'categorias': [cat.nombre for cat in self.categorias],
            'num_me_gustas': self.contar_me_gustas(),
            'ingredientes': [
                {
                    'nombre': ri.ingrediente.nombre,
                    'cantidad': ri.cantidad,
                    'unidad': ri.ingrediente.unidad_medida
                } for ri in self.ingredientes
            ],
            'instrucciones': [
                {
                    'numero_paso': inst.numero_paso,
                    'descripcion': inst.descripcion
                } for inst in sorted(self.instrucciones, key=lambda x: x.numero_paso)
            ]
        }