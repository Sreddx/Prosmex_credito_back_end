from flask import Blueprint, request, jsonify
from app.services.corte_service import CorteService
from flask_jwt_extended import jwt_required
from app.services.usuario_service import UsuarioService

cortes_blueprint = Blueprint('corte', __name__, url_prefix='/cortes')

@cortes_blueprint.route('/cortes', methods=['POST'])
@jwt_required()  # Requiere autenticación por JWT
def create_corte():
    """
    Endpoint para crear un corte. El usuario se obtiene del JWT.
    """
    data = request.get_json()

    try:
        # Obtener el usuario desde el JWT
        usuario = UsuarioService.get_user_from_jwt()
        

        # Crear el corte con el usuario autenticado y el grupo relacionado
        corte_service = CorteService()
        new_corte = corte_service.create_corte(data, usuario.id)
        return jsonify(new_corte.serialize()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@cortes_blueprint.route('/cortes/<int:corte_id>', methods=['GET'])
@jwt_required()
def get_corte(corte_id):
    """
    Endpoint para obtener un corte por su ID.
    """
    try:
        corte_service = CorteService(corte_id)
        corte = corte_service.get_corte()
        return jsonify(corte.serialize()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@cortes_blueprint.route('/cortes/<int:corte_id>', methods=['PUT'])
@jwt_required()
def update_corte(corte_id):
    """
    Endpoint para actualizar un corte.
    """
    data = request.get_json()
    try:
        corte_service = CorteService(corte_id)
        updated_corte = corte_service.update_corte(data)
        if not updated_corte:
            return jsonify({"error": "Corte no encontrado"}), 404
        return jsonify(updated_corte.serialize()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@cortes_blueprint.route('/cortes/<int:corte_id>', methods=['DELETE'])
@jwt_required()
def delete_corte(corte_id):
    """
    Endpoint para eliminar un corte.
    """
    try:
        corte_service = CorteService(corte_id)
        corte_service.delete_corte()
        return jsonify({"message": "Corte eliminado"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@cortes_blueprint.route('/cortes', methods=['GET'])
@jwt_required()
def list_cortes():
    """
    Endpoint para listar todos los cortes.
    """
    try:
        corte_service = CorteService()
        cortes = corte_service.list_cortes()
        return jsonify(cortes), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# ENDPOINTS PARA PANTALLA DE CORTE
# 