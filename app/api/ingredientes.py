from flask import request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Ingrediente
from app.config.db import db
from . import api_bp

@api_bp.route('/ingredientes')
def listar_ingredientes():
    ingredientes = Ingrediente.query.all()
    return render_template('ingredientes.html', ingredientes=ingredientes)

# Rutas para administración de ingredientes (solo para administradores)
@api_bp.route('/admin/ingredientes', methods=['GET', 'POST'])
@login_required
def admin_ingredientes():
    # Verificar si el usuario es administrador
    if current_user.id != 1:  # Suponiendo que el ID 1 es el administrador
        flash('No tienes permisos para acceder a esta sección', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'GET':
        ingredientes = Ingrediente.query.all()
        return render_template('admin/ingredientes.html', ingredientes=ingredientes)
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        unidad_medida = request.form.get('unidad_medida')
        
        if not nombre:
            flash('El nombre del ingrediente es obligatorio', 'error')
            return redirect(url_for('api.admin_ingredientes'))
        
        # Verificar si el ingrediente ya existe
        ingrediente_existente = Ingrediente.query.filter_by(nombre=nombre).first()
        if ingrediente_existente:
            flash('Ya existe un ingrediente con ese nombre', 'error')
            return redirect(url_for('api.admin_ingredientes'))
        
        # Crear nuevo ingrediente
        nuevo_ingrediente = Ingrediente(nombre=nombre, unidad_medida=unidad_medida)
        db.session.add(nuevo_ingrediente)
        db.session.commit()
        
        flash('Ingrediente creado exitosamente', 'success')
        return redirect(url_for('api.admin_ingredientes'))

@api_bp.route('/admin/ingredientes/<int:ingrediente_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_ingrediente(ingrediente_id):
    # Verificar si el usuario es administrador
    if current_user.id != 1:  # Suponiendo que el ID 1 es el administrador
        flash('No tienes permisos para acceder a esta sección', 'error')
        return redirect(url_for('main.index'))
    
    ingrediente = Ingrediente.query.get_or_404(ingrediente_id)
    
    if request.method == 'GET':
        return render_template('admin/editar_ingrediente.html', ingrediente=ingrediente)
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        unidad_medida = request.form.get('unidad_medida')
        
        if not nombre:
            flash('El nombre del ingrediente es obligatorio', 'error')
            return redirect(url_for('api.editar_ingrediente', ingrediente_id=ingrediente_id))
        
        # Verificar si el nombre ya existe y no es el mismo que se está editando
        ingrediente_existente = Ingrediente.query.filter_by(nombre=nombre).first()
        if ingrediente_existente and ingrediente_existente.id != ingrediente_id:
            flash('Ya existe un ingrediente con ese nombre', 'error')
            return redirect(url_for('api.editar_ingrediente', ingrediente_id=ingrediente_id))
        
        # Actualizar ingrediente
        ingrediente.nombre = nombre
        ingrediente.unidad_medida = unidad_medida
        db.session.commit()
        
        flash('Ingrediente actualizado exitosamente', 'success')
        return redirect(url_for('api.admin_ingredientes'))

@api_bp.route('/admin/ingredientes/<int:ingrediente_id>/eliminar', methods=['POST'])
@login_required
def eliminar_ingrediente(ingrediente_id):
    # Verificar si el usuario es administrador
    if current_user.id != 1:  # Suponiendo que el ID 1 es el administrador
        flash('No tienes permisos para acceder a esta sección', 'error')
        return redirect(url_for('main.index'))
    
    ingrediente = Ingrediente.query.get_or_404(ingrediente_id)
    
    # Verificar si el ingrediente está en uso
    recetas_con_ingrediente = ingrediente.recetas_ingredientes
    if recetas_con_ingrediente:
        flash('No se puede eliminar el ingrediente porque está siendo utilizado por recetas', 'error')
        return redirect(url_for('api.admin_ingredientes'))
    
    # Eliminar ingrediente
    db.session.delete(ingrediente)
    db.session.commit()
    
    flash('Ingrediente eliminado exitosamente', 'success')
    return redirect(url_for('api.admin_ingredientes'))

@api_bp.route('/api/ingredientes/buscar')
def buscar_ingredientes():
    """Endpoint para búsqueda de ingredientes con autocomplete"""
    termino = request.args.get('term', '')
    
    if not termino:
        return jsonify([])
    
    ingredientes = Ingrediente.query.filter(
        Ingrediente.nombre.like(f'%{termino}%')
    ).limit(10).all()
    
    resultado = [
        {
            'id': ing.id,
            'value': ing.nombre,
            'label': f"{ing.nombre} ({ing.unidad_medida})",
            'unidad_medida': ing.unidad_medida
        } for ing in ingredientes
    ]
    
    return jsonify(resultado)