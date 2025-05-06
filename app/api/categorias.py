from flask import request, jsonify, render_template, redirect, url_for, flash, current_app
from flask_login import current_user
from app.models import Categoria
from app.config.db import db
import sqlalchemy.exc
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

# Endpoint para editar o actualizar una categoría ✅
@api_bp.route('/admin/categorias/<int:categoria_id>/editar', methods=['GET', 'PUT'])
# @login_required
def editar_categoria(categoria_id):
    try:
        categoria = Categoria.query.get(categoria_id)
        if not categoria:
            if request.is_json:
                return jsonify({
                    'status': 'error',
                    'message': 'Categoría no encontrada',
                    'error_type': 'not_found',
                    'categoria_id': categoria_id
                }), 404
            else:
                flash('Categoría no encontrada', 'error')
                return redirect(url_for('api.admin_categorias'))
        
        if request.method == 'GET':
            formato = request.args.get('format', 'json')
            
            if formato == 'html':
                return render_template('admin/editar_categoria.html', categoria=categoria)
            else:
                respuesta = {
                    'status': 'success',
                    'categoria': {
                        'id': categoria.id,
                        'nombre': categoria.nombre,
                        'descripcion': categoria.descripcion,
                        'total_recetas': categoria.recetas.count() if hasattr(categoria, 'recetas') else 0
                    }
                }
                
                return jsonify(respuesta), 200
        
        elif request.method == 'PUT':
            try:
                # Determinar si es JSON o form-data
                if request.is_json:
                    data = request.get_json()
                    nombre = data.get('nombre')
                    descripcion = data.get('descripcion')
                else:
                    nombre = request.form.get('nombre')
                    descripcion = request.form.get('descripcion')
                
                # Validar datos
                if not nombre:
                    if request.is_json:
                        return jsonify({
                            'status': 'error',
                            'message': 'El nombre de la categoría es obligatorio',
                            'error_type': 'validation_error',
                            'field': 'nombre'
                        }), 400
                    else:
                        flash('El nombre de la categoría es obligatorio', 'error')
                        return redirect(url_for('api.editar_categoria', categoria_id=categoria_id))
                
                # Verificar si el nombre ya existe y no es el mismo que se está editando
                categoria_existente = Categoria.query.filter_by(nombre=nombre).first()
                if categoria_existente and categoria_existente.id != categoria_id:
                    if request.is_json:
                        return jsonify({
                            'status': 'error',
                            'message': 'Ya existe una categoría con ese nombre',
                            'error_type': 'duplicate_error',
                            'field': 'nombre',
                            'existing_id': categoria_existente.id
                        }), 409  # 409 Conflict
                    else:
                        flash('Ya existe una categoría con ese nombre', 'error')
                        return redirect(url_for('api.editar_categoria', categoria_id=categoria_id))
                
                try:
                    # Guardar datos actualizados
                    categoria.nombre = nombre
                    categoria.descripcion = descripcion
                    db.session.commit()
                    
                    if request.is_json:
                        return jsonify({
                            'status': 'success',
                            'message': 'Categoría actualizada exitosamente',
                            'categoria': {
                                'id': categoria.id,
                                'nombre': categoria.nombre,
                                'descripcion': categoria.descripcion,
                                'total_recetas': categoria.recetas.count() if hasattr(categoria, 'recetas') else 0
                            }
                        }), 200
                    else:
                        flash('Categoría actualizada exitosamente', 'success')
                        return redirect(url_for('api.admin_categorias'))
                
                except sqlalchemy.exc.IntegrityError as e:
                    db.session.rollback()
                    current_app.logger.error(f"Error de integridad al actualizar categoría {categoria_id}: {str(e)}")
                    
                    if request.is_json:
                        return jsonify({
                            'status': 'error',
                            'message': 'Error de integridad en la base de datos',
                            'error_type': 'integrity_error',
                            'details': str(e) if current_app.debug else 'Error al guardar en la base de datos'
                        }), 400
                    else:
                        flash('Error al actualizar la categoría: posible duplicado', 'error')
                        return redirect(url_for('api.editar_categoria', categoria_id=categoria_id))
                
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error(f"Error al actualizar categoría {categoria_id}: {str(e)}")
                    
                    if request.is_json:
                        return jsonify({
                            'status': 'error',
                            'message': 'Error al actualizar la categoría',
                            'error_type': 'database_error',
                            'details': str(e) if current_app.debug else 'Error en la base de datos'
                        }), 500
                    else:
                        flash('Error al actualizar la categoría', 'error')
                        return redirect(url_for('api.editar_categoria', categoria_id=categoria_id))
            
            except Exception as e:
                current_app.logger.error(f"Error general al procesar solicitud POST para editar categoría {categoria_id}: {str(e)}")
                
                if request.is_json:
                    return jsonify({
                        'status': 'error',
                        'message': 'Error al procesar la solicitud',
                        'error_type': 'request_processing_error',
                        'details': str(e) if current_app.debug else 'Error interno del servidor'
                    }), 500
                else:
                    flash('Error al procesar la solicitud', 'error')
                    return redirect(url_for('api.editar_categoria', categoria_id=categoria_id))
        
        else:
            # Método no permitido
            return jsonify({
                'status': 'error',
                'message': 'Método no permitido',
                'error_type': 'method_not_allowed'
            }), 405
    
    except Exception as e:
        # Error general
        current_app.logger.error(f"Error general en endpoint editar_categoria para ID {categoria_id}: {str(e)}")
        
        if request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Error interno del servidor',
                'error_type': 'server_error',
                'details': str(e) if current_app.debug else 'Error interno del servidor'
            }), 500
        else:
            flash('Error del servidor', 'error')
            return redirect(url_for('api.admin_categorias'))

# Endpoint para eliminar una categoría ✅
@api_bp.route('/admin/categorias/<int:categoria_id>/eliminar', methods=['POST', 'DELETE'])
# @login_required
def eliminar_categoria(categoria_id):
    try:
        categoria = Categoria.query.get(categoria_id)
        if not categoria:
            if request.is_json or request.method == 'DELETE':
                return jsonify({
                    'status': 'error',
                    'message': 'Categoría no encontrada',
                    'error_type': 'not_found',
                    'categoria_id': categoria_id
                }), 404
            else:
                flash('Categoría no encontrada', 'error')
                return redirect(url_for('api.admin_categorias'))
        
        try:
            recetas_count = categoria.recetas.count() if hasattr(categoria, 'recetas') else 0
            
            if recetas_count > 0:
                recetas_ids = [receta.id for receta in categoria.recetas]
                current_app.logger.info(f"Intento de eliminar categoría {categoria_id} usada en {recetas_count} recetas: {recetas_ids[:5]}...")
                
                if request.is_json or request.method == 'DELETE':
                    return jsonify({
                        'status': 'error',
                        'message': 'No se puede eliminar la categoría porque está siendo utilizada por recetas',
                        'error_type': 'constraint_violation',
                        'categoria_id': categoria_id,
                        'recetas_count': recetas_count,
                        'recetas_ids': recetas_ids[:10]
                    }), 409
                else:
                    flash('No se puede eliminar la categoría porque está siendo utilizada por recetas', 'error')
                    return redirect(url_for('api.admin_categorias'))
            
            try:
                nombre_categoria = categoria.nombre
                db.session.delete(categoria)
                db.session.commit()
                current_app.logger.info(f"Categoría {categoria_id} ({nombre_categoria}) eliminada exitosamente")
                
                if request.is_json or request.method == 'DELETE':
                    return jsonify({
                        'status': 'success',
                        'message': 'Categoría eliminada exitosamente',
                        'categoria_id': categoria_id,
                        'categoria_nombre': nombre_categoria
                    }), 200
                else:
                    flash('Categoría eliminada exitosamente', 'success')
                    return redirect(url_for('api.admin_categorias'))
                
            except sqlalchemy.exc.IntegrityError as e:
                db.session.rollback()
                current_app.logger.error(f"Error de integridad al eliminar categoría {categoria_id}: {str(e)}")
                
                if request.is_json or request.method == 'DELETE':
                    return jsonify({
                        'status': 'error',
                        'message': 'Error de integridad en la base de datos',
                        'error_type': 'integrity_error',
                        'details': str(e) if current_app.debug else 'Error al eliminar de la base de datos'
                    }), 400
                else:
                    flash('Error al eliminar la categoría: violación de integridad', 'error')
                    return redirect(url_for('api.admin_categorias'))
                
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error al eliminar categoría {categoria_id}: {str(e)}")
                
                if request.is_json or request.method == 'DELETE':
                    return jsonify({
                        'status': 'error',
                        'message': 'Error al eliminar la categoría',
                        'error_type': 'database_error',
                        'details': str(e) if current_app.debug else 'Error en la base de datos'
                    }), 500
                else:
                    flash('Error al eliminar la categoría', 'error')
                    return redirect(url_for('api.admin_categorias'))
                
        except Exception as e:
            current_app.logger.error(f"Error al verificar uso de la categoría {categoria_id}: {str(e)}")
            
            if request.is_json or request.method == 'DELETE':
                return jsonify({
                    'status': 'error',
                    'message': 'Error al verificar uso de la categoría',
                    'error_type': 'verification_error',
                    'details': str(e) if current_app.debug else 'Error al verificar relaciones'
                }), 500
            else:
                flash('Error al verificar uso de la categoría', 'error')
                return redirect(url_for('api.admin_categorias'))
                
    except Exception as e:
        current_app.logger.error(f"Error general en endpoint eliminar_categoria para ID {categoria_id}: {str(e)}")
        
        if request.is_json or request.method == 'DELETE':
            return jsonify({
                'status': 'error',
                'message': 'Error interno del servidor',
                'error_type': 'server_error',
                'details': str(e) if current_app.debug else 'Error interno del servidor'
            }), 500
        else:
            flash('Error del servidor', 'error')
            return redirect(url_for('api.admin_categorias'))