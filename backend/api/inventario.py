# API de Gestión de Inventario
# Centro Minero SENA

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .blueprints import inventario_bp
from ..utils.database import DatabaseManager
from ..utils.helpers import generar_id

db = DatabaseManager()

@inventario_bp.route('', methods=['GET'])
@jwt_required()
def listar_inventario():
    """GET /api/inventario - Listar todos los items"""
    try:
        query = """
            SELECT id, nombre, categoria, cantidad_actual, cantidad_minima, 
            unidad, proveedor, ubicacion,
            DATE_FORMAT(fecha_vencimiento, '%Y-%m-%d') as fecha_vencimiento
            FROM inventario 
            ORDER BY nombre
        """
        items = db.ejecutar_query(query)
        
        # Calcular nivel de stock
        for item in items:
            if item['cantidad_actual'] <= item['cantidad_minima']:
                item['nivel_stock'] = 'critico'
            elif item['cantidad_actual'] <= item['cantidad_minima'] * 1.5:
                item['nivel_stock'] = 'bajo'
            else:
                item['nivel_stock'] = 'normal'
        
        return jsonify({'success': True, 'items': items}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error listando inventario: {str(e)}'}), 500

@inventario_bp.route('/critico', methods=['GET'])
@jwt_required()
def items_criticos():
    """GET /api/inventario/critico - Items con stock crítico"""
    try:
        query = """
            SELECT id, nombre, categoria, cantidad_actual, cantidad_minima
            FROM inventario 
            WHERE cantidad_actual <= cantidad_minima
            ORDER BY cantidad_actual ASC
        """
        items = db.ejecutar_query(query)
        
        return jsonify({'success': True, 'items_criticos': items}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error obteniendo items críticos: {str(e)}'}), 500

@inventario_bp.route('/<string:item_id>', methods=['GET'])
@jwt_required()
def obtener_item(item_id):
    """GET /api/inventario/{id} - Obtener item específico"""
    try:
        query = """
            SELECT id, nombre, categoria, cantidad_actual, cantidad_minima, 
            unidad, proveedor, ubicacion, descripcion,
            DATE_FORMAT(fecha_vencimiento, '%Y-%m-%d') as fecha_vencimiento
            FROM inventario WHERE id = %s
        """
        item = db.obtener_uno(query, (item_id,))
        
        if not item:
            return jsonify({'error': 'Item no encontrado'}), 404
        
        return jsonify({'success': True, 'item': item}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error obteniendo item: {str(e)}'}), 500

@inventario_bp.route('', methods=['POST'])
@jwt_required()
def crear_item():
    """POST /api/inventario - Crear nuevo item"""
    try:
        data = request.get_json()
        
        if not data or 'nombre' not in data or 'categoria' not in data:
            return jsonify({'error': 'Nombre y categoría son requeridos'}), 400
        
        item_id = generar_id('INV', 8)
        
        datos_item = {
            'id': item_id,
            'nombre': data['nombre'],
            'categoria': data['categoria'],
            'cantidad_actual': data.get('cantidad_actual', 0),
            'cantidad_minima': data.get('cantidad_minima', 0),
            'unidad': data.get('unidad', 'unidades'),
            'proveedor': data.get('proveedor'),
            'ubicacion': data.get('ubicacion')
        }
        
        db.insertar('inventario', datos_item)
        
        return jsonify({
            'success': True,
            'message': 'Item creado exitosamente',
            'item_id': item_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Error creando item: {str(e)}'}), 500

@inventario_bp.route('/<string:item_id>/agregar', methods=['POST'])
@jwt_required()
def agregar_cantidad(item_id):
    """POST /api/inventario/{id}/agregar - Agregar cantidad"""
    try:
        data = request.get_json()
        
        if not data or 'cantidad' not in data:
            return jsonify({'error': 'Cantidad es requerida'}), 400
        
        cantidad = int(data['cantidad'])
        if cantidad <= 0:
            return jsonify({'error': 'Cantidad debe ser positiva'}), 400
        
        # Obtener cantidad actual
        item = db.obtener_uno('SELECT cantidad_actual FROM inventario WHERE id = %s', (item_id,))
        if not item:
            return jsonify({'error': 'Item no encontrado'}), 404
        
        nueva_cantidad = item['cantidad_actual'] + cantidad
        db.actualizar('inventario', {'cantidad_actual': nueva_cantidad}, 'id = %s', (item_id,))
        
        return jsonify({
            'success': True,
            'message': f'Se agregaron {cantidad} unidades',
            'nueva_cantidad': nueva_cantidad
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error agregando cantidad: {str(e)}'}), 500

@inventario_bp.route('/<string:item_id>/retirar', methods=['POST'])
@jwt_required()
def retirar_cantidad(item_id):
    """POST /api/inventario/{id}/retirar - Retirar cantidad"""
    try:
        data = request.get_json()
        
        if not data or 'cantidad' not in data:
            return jsonify({'error': 'Cantidad es requerida'}), 400
        
        cantidad = int(data['cantidad'])
        if cantidad <= 0:
            return jsonify({'error': 'Cantidad debe ser positiva'}), 400
        
        # Obtener cantidad actual
        item = db.obtener_uno('SELECT cantidad_actual FROM inventario WHERE id = %s', (item_id,))
        if not item:
            return jsonify({'error': 'Item no encontrado'}), 404
        
        if item['cantidad_actual'] < cantidad:
            return jsonify({'error': 'Cantidad insuficiente en inventario'}), 400
        
        nueva_cantidad = item['cantidad_actual'] - cantidad
        db.actualizar('inventario', {'cantidad_actual': nueva_cantidad}, 'id = %s', (item_id,))
        
        return jsonify({
            'success': True,
            'message': f'Se retiraron {cantidad} unidades',
            'nueva_cantidad': nueva_cantidad
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retirando cantidad: {str(e)}'}), 500
