from flask import request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Usuario, Seguidor
from app.config.db import db
from . import api_bp

@api_bp.route('/seguidores/sugeridos')
@login_required
def sugerir_usuarios():
    """Muestra usuarios sugeridos para seguir (usuarios que no sigues)"""
    
    # Obtener IDs de usuarios que ya sigues
    seguidos_ids = [seguido.usuario_id for seguido in current_user.seguidos.all()]
    
    # Añadir tu propio ID a la lista
    seguidos_ids.append(current_user.id)
    
    # Obtener usuarios que no sigues (limitado a 10)
    usuarios_sugeridos = Usuario.query.filter(
        ~Usuario.id.in_(seguidos_ids)
    ).limit(10).all()
    
    return render_template('sugerencias.html', usuarios=usuarios_sugeridos)

@api_bp.route('/usuarios/<int:usuario_id>/seguir', methods=['POST'])
@login_required
def seguir(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if usuario.id == current_user.id:
        flash('No puedes seguirte a ti mismo', 'error')
        return redirect(url_for('api.ver_perfil', usuario_id=usuario_id))
    
    # Verificar si ya sigues a este usuario
    seguidor_existente = Seguidor.query.filter_by(
        usuario_id=usuario.id,
        seguidor_id=current_user.id
    ).first()
    
    if seguidor_existente:
        flash('Ya sigues a este usuario', 'info')
    else:
        nuevo_seguidor = Seguidor(
            usuario_id=usuario.id,
            seguidor_id=current_user.id
        )
        db.session.add(nuevo_seguidor)
        db.session.commit()
        flash(f'Ahora sigues a {usuario.nombre}', 'success')
    
    return redirect(url_for('api.ver_perfil', usuario_id=usuario_id))

@api_bp.route('/usuarios/<int:usuario_id>/dejar-seguir', methods=['POST'])
@login_required
def dejar_seguir(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    
    # Buscar relación de seguidor
    seguidor = Seguidor.query.filter_by(
        usuario_id=usuario.id,
        seguidor_id=current_user.id
    ).first()
    
    if seguidor:
        db.session.delete(seguidor)
        db.session.commit()
        flash(f'Has dejado de seguir a {usuario.nombre}', 'info')
    else:
        flash('No sigues a este usuario', 'info')
    
    return redirect(url_for('api.ver_perfil', usuario_id=usuario_id))

@api_bp.route('/api/usuarios/seguidores/<int:usuario_id>')
def api_obtener_seguidores(usuario_id):
    """API para obtener seguidores de un usuario"""
    usuario = Usuario.query.get_or_404(usuario_id)
    seguidores = usuario.get_seguidores()
    
    return jsonify({
        'seguidores': [
            {
                'id': seguidor.id,
                'nombre': seguidor.nombre,
                'foto_perfil': seguidor.foto_perfil
            } for seguidor in seguidores
        ]
    })

@api_bp.route('/api/usuarios/seguidos/<int:usuario_id>')
def api_obtener_seguidos(usuario_id):
    """API para obtener usuarios seguidos por un usuario"""
    usuario = Usuario.query.get_or_404(usuario_id)
    seguidos = usuario.get_seguidos()
    
    return jsonify({
        'seguidos': [
            {
                'id': seguido.id,
                'nombre': seguido.nombre,
                'foto_perfil': seguido.foto_perfil
            } for seguido in seguidos
        ]
    })