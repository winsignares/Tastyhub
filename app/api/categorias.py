from flask import request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Categoria
from app.config.db import db
from . import api_bp

@api_bp.route('/categorias')
def listar_categorias():
    categorias = Categoria.query.all()
    return render_template('categorias.html', categorias=categorias)

@api_bp.route('/categorias/<int:categoria_id>')
def ver_categoria(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)
    recetas = categoria.recetas.all()
    return render_template('categoria.html', categoria=categoria, recetas=recetas)

# Rutas para administración de categorías (solo para administradores)
@api_bp.route('/admin/categorias', methods=['GET', 'POST'])
@login_required
def admin_categorias():
    # Verificar si el usuario es administrador (esto se podría mejorar con un decorador)
    if current_user.id != 1:  # Suponiendo que el ID 1 es el administrador
        flash('No tienes permisos para acceder a esta sección', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'GET':
        categorias = Categoria.query.all()
        return render_template('admin/categorias.html', categorias=categorias)
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        
        if not nombre:
            flash('El nombre de la categoría es obligatorio', 'error')
            return redirect(url_for('api.admin_categorias'))
        
        # Verificar si la categoría ya existe
        categoria_existente = Categoria.query.filter_by(nombre=nombre).first()
        if categoria_existente:
            flash('Ya existe una categoría con ese nombre', 'error')
            return redirect(url_for('api.admin_categorias'))
        
        # Crear nueva categoría
        nueva_categoria = Categoria(nombre=nombre, descripcion=descripcion)
        db.session.add(nueva_categoria)
        db.session.commit()
        
        flash('Categoría creada exitosamente', 'success')
        return redirect(url_for('api.admin_categorias'))

@api_bp.route('/admin/categorias/<int:categoria_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_categoria(categoria_id):
    # Verificar si el usuario es administrador
    if current_user.id != 1:  # Suponiendo que el ID 1 es el administrador
        flash('No tienes permisos para acceder a esta sección', 'error')
        return redirect(url_for('main.index'))
    
    categoria = Categoria.query.get_or_404(categoria_id)
    
    if request.method == 'GET':
        return render_template('admin/editar_categoria.html', categoria=categoria)
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        
        if not nombre:
            flash('El nombre de la categoría es obligatorio', 'error')
            return redirect(url_for('api.editar_categoria', categoria_id=categoria_id))
        
        # Verificar si el nombre ya existe y no es el mismo que se está editando
        categoria_existente = Categoria.query.filter_by(nombre=nombre).first()
        if categoria_existente and categoria_existente.id != categoria_id:
            flash('Ya existe una categoría con ese nombre', 'error')
            return redirect(url_for('api.editar_categoria', categoria_id=categoria_id))
        
        # Actualizar categoría
        categoria.nombre = nombre
        categoria.descripcion = descripcion
        db.session.commit()
        
        flash('Categoría actualizada exitosamente', 'success')
        return redirect(url_for('api.admin_categorias'))

@api_bp.route('/admin/categorias/<int:categoria_id>/eliminar', methods=['POST'])
@login_required
def eliminar_categoria(categoria_id):
    # Verificar si el usuario es administrador
    if current_user.id != 1:  # Suponiendo que el ID 1 es el administrador
        flash('No tienes permisos para acceder a esta sección', 'error')
        return redirect(url_for('main.index'))
    
    categoria = Categoria.query.get_or_404(categoria_id)
    
    # Verificar si la categoría está en uso
    if categoria.recetas.count() > 0:
        flash('No se puede eliminar la categoría porque está siendo utilizada por recetas', 'error')
        return redirect(url_for('api.admin_categorias'))
    
    # Eliminar categoría
    db.session.delete(categoria)
    db.session.commit()
    
    flash('Categoría eliminada exitosamente', 'success')
    return redirect(url_for('api.admin_categorias'))