from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.services import PrestamoService
from app.services import UsuarioService
from app.services import PagoService
from app.blueprints.helpers import create_response, make_error_response, handle_exceptions

prestamo_blueprint = Blueprint('prestamo', __name__, url_prefix='/prestamos')

@prestamo_blueprint.route('/', methods=['POST'])
@jwt_required()
def create_prestamo():
    def func():
        data = request.get_json()
        prestamo_service = PrestamoService()
        user = UsuarioService.get_user_from_jwt()
        if not user:
            raise ValueError("Usuario no encontrado")
        if not data:
            raise ValueError("No se proporcionaron datos para prestamo")
        new_prestamo = prestamo_service.create_prestamo(data, user)
        return create_response({'message': 'Prestamo created successfully', 'prestamo': new_prestamo.prestamo_id}, 201)

    return handle_exceptions(func)

@prestamo_blueprint.route('/<int:prestamo_id>', methods=['GET'])
def get_prestamo(prestamo_id):
    def func():
        prestamo_service = PrestamoService(prestamo_id)
        prestamo = prestamo_service.get_prestamo()
        if prestamo:
            return create_response(prestamo.serialize(), 200)
        else:
            return make_error_response('Prestamo not found', 404)

    return handle_exceptions(func)

@prestamo_blueprint.route('/<int:prestamo_id>', methods=['PUT'])
def update_prestamo(prestamo_id):
    def func():
        data = request.get_json()
        prestamo_service = PrestamoService(prestamo_id)
        updated_prestamo = prestamo_service.update_prestamo(data)
        if updated_prestamo:
            return create_response({'message': 'Prestamo updated successfully', 'prestamo': updated_prestamo.prestamo_id}, 200)
        else:
            return make_error_response('Prestamo not found', 404)

    return handle_exceptions(func)

@prestamo_blueprint.route('/<int:prestamo_id>', methods=['DELETE'])
def delete_prestamo(prestamo_id):
    def func():
        prestamo_service = PrestamoService(prestamo_id)
        success = prestamo_service.delete_prestamo()
        if success:
            return create_response({'message': 'Prestamo deleted successfully'}, 200)
        else:
            return make_error_response('Prestamo not found', 404)

    return handle_exceptions(func)

@prestamo_blueprint.route('/', methods=['GET'])
def list_prestamos():
    def func():
        prestamo_service = PrestamoService()
        prestamos = prestamo_service.list_prestamos()
        return create_response(prestamos, 200)

    return handle_exceptions(func)

@prestamo_blueprint.route('/tipos', methods=['GET'])
def list_tipos_prestamo():
    def func():
        prestamo_service = PrestamoService()
        tipos_prestamo = prestamo_service.list_tipos_prestamo()
        return create_response(tipos_prestamo, 200)

    return handle_exceptions(func)

@prestamo_blueprint.route('/<int:prestamo_id>/cobranza-ideal', methods=['GET'])
def get_cobranza_ideal(prestamo_id):
    """
    Endpoint para obtener la cobranza ideal semanal de un préstamo por su ID.
    """
    def func():
        prestamo_service = PrestamoService(prestamo_id)
        prestamo = prestamo_service.get_prestamo()
        if prestamo:
            # Calcular la cobranza ideal
            cobranza_ideal = prestamo.calcular_cobranza_ideal()
            return create_response({'prestamo_id': prestamo.prestamo_id, 'cobranza_ideal': cobranza_ideal}, 200)
        else:
            return make_error_response('Prestamo not found', 404)

    return handle_exceptions(func)
