from flask import request, jsonify, render_template, redirect, url_for, flash
from flask_login import current_user
from app.models import Categoria
from app.config.db import db
from . import api_bp

# Endpoints para la gestión de categorías de recetas ✅
@api_bp.route('/categorias')
def listar_categorias():
    try:
        categorias = Categoria.query.all()
        formato = request.args.get('format', 'json')
        if formato == 'html':
            return render_template('categorias.html', categorias=categorias)
        else:
            respuesta = {
                'status': 'success',
                'total': len(categorias),
                'categorias': [
                    {
                        'id': categoria.id,
                        'nombre': categoria.nombre,
                        'descripcion': categoria.descripcion,
                        'total_recetas': categoria.recetas.count() if hasattr(categoria, 'recetas') else 0
                    } for categoria in categorias
                ]
            }
            
            return jsonify(respuesta), 200
            
    except sqlalchemy.exc.SQLAlchemyError as e:
        # Error específico de base de datos
        current_app.logger.error(f"Error de base de datos al listar categorías: {str(e)}")
        
        return jsonify({
            'status': 'error',
            'message': 'Error al obtener categorías desde la base de datos',
            'error_type': 'database_error',
            'details': str(e) if current_app.debug else 'Error en la consulta a la base de datos'
        }), 500
        
    except Exception as e:
        # Error general
        current_app.logger.error(f"Error general al listar categorías: {str(e)}")
        
        return jsonify({
            'status': 'error',
            'message': 'Error al procesar la solicitud',
            'error_type': 'server_error',
            'details': str(e) if current_app.debug else 'Error interno del servidor'
        }), 500
    # return render_template('categorias.html', categorias=categorias)

# Endpoint para obtener una categoría específica y sus recetas ✅
@api_bp.route('/categorias/<int:categoria_id>')
def ver_categoria(categoria_id):
    try:
        categoria = Categoria.query.get(categoria_id)
        if not categoria:
            return jsonify({
                'status': 'error',
                'message': 'Categoría no encontrada',
                'error_type': 'not_found',
                'categoria_id': categoria_id
            }), 404
        
        try:
            recetas = categoria.recetas.all() if hasattr(categoria, 'recetas') else []
            formato = request.args.get('format', 'json')
            
            if formato == 'html':
                return render_template('categoria.html', categoria=categoria, recetas=recetas)
            else:
                # Crear respuesta JSON
                respuesta = {
                    'status': 'success',
                    'categoria': {
                        'id': categoria.id,
                        'nombre': categoria.nombre,
                        'descripcion': categoria.descripcion,
                        'total_recetas': len(recetas)
                    },
                    'recetas': [
                        {
                            'id': receta.id,
                            'titulo': receta.titulo,
                            'descripcion': receta.descripcion,
                            'imagen_portada': receta.imagen_portada,
                            'tiempo_preparacion': receta.tiempor_pre,
                            'fecha_creacion': receta.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
                            'autor_id': receta.id_usuario,
                            'autor_nombre': receta.autor.nombre if hasattr(receta, 'autor') and receta.autor else None,
                            'total_me_gustas': receta.contar_me_gustas() if hasattr(receta, 'contar_me_gustas') else 0
                        } for receta in recetas
                    ]
                }
                
                return jsonify(respuesta), 200
                
        except AttributeError as e:
            # Error específico para cuando la relación recetas no está disponible
            current_app.logger.error(f"Error de atributo al obtener recetas de categoría {categoria_id}: {str(e)}")
            
            # Crear una respuesta parcial con los datos de la categoría
            respuesta_parcial = {
                'status': 'partial_success',
                'message': 'Categoría encontrada pero hubo problemas al obtener las recetas asociadas',
                'categoria': {
                    'id': categoria.id,
                    'nombre': categoria.nombre,
                    'descripcion': categoria.descripcion
                },
                'error_details': str(e) if current_app.debug else 'Error al obtener las recetas asociadas'
            }
            
            return jsonify(respuesta_parcial), 206  # 206 Partial Content
            
    except sqlalchemy.exc.SQLAlchemyError as e:
        # Error específico de SQLAlchemy
        current_app.logger.error(f"Error de base de datos al obtener categoría {categoria_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error de base de datos',
            'error_type': 'database_error',
            'details': str(e) if current_app.debug else 'Error en la consulta a la base de datos'
        }), 500
        
    except Exception as e:
        # Error general
        current_app.logger.error(f"Error general al obtener categoría {categoria_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error al procesar la solicitud',
            'error_type': 'server_error',
            'details': str(e) if current_app.debug else 'Error interno del servidor'
        }), 500

# Rutas para administración de categorías (solo para administradores)
@api_bp.route('/admin/categorias', methods=['GET', 'POST'])
# @login_required
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
# @login_required
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
# @login_required
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