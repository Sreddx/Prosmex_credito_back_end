from flask import Blueprint, request
from app.services import ClienteAvalService
from app.blueprints.helpers import create_response, make_error_response, handle_exceptions

cliente_blueprint = Blueprint('cliente', __name__, url_prefix='/clientes')

@cliente_blueprint.route('/', methods=['POST'])
def create_cliente():
    def func():
        data = request.get_json()
        cliente_service = ClienteAvalService()
        new_cliente = cliente_service.create_cliente(data)
        return create_response({'message': 'Cliente created successfully', 'cliente': new_cliente.titular_id}, 201)

    return handle_exceptions(func)

@cliente_blueprint.route('/<int:cliente_id>', methods=['GET'])
def get_cliente(cliente_id):
    def func():
        cliente_service = ClienteAvalService(cliente_id)
        cliente = cliente_service.get_cliente()
        if cliente:
            return create_response(cliente.serialize(), 200)
        else:
            return make_error_response('Cliente not found', 404)
    
    return handle_exceptions(func)

@cliente_blueprint.route('/<int:cliente_id>', methods=['PUT'])
def update_cliente(cliente_id):
    def func():
        data = request.get_json()
        cliente_service = ClienteAvalService(cliente_id)
        updated_cliente = cliente_service.update_cliente(data)
        if updated_cliente:
            return create_response({'message': 'Cliente updated successfully', 'cliente': updated_cliente.titular_id}, 200)
        else:
            return make_error_response('Cliente not found', 404)

    return handle_exceptions(func)

@cliente_blueprint.route('/<int:cliente_id>', methods=['DELETE'])
def delete_cliente(cliente_id):
    def func():
        cliente_service = ClienteAvalService(cliente_id)
        success = cliente_service.delete_cliente()
        if success:
            return create_response({'message': 'Cliente deleted successfully'}, 200)
        else:
            return make_error_response('Cliente not found', 404)

    return handle_exceptions(func)

@cliente_blueprint.route('/', methods=['GET'])
def list_clientes():
    def func():
        cliente_service = ClienteAvalService()
        clientes = cliente_service.list_clientes()
        return create_response([cliente.serialize() for cliente in clientes], 200)

    return handle_exceptions(func)

# List avales para prestamo
@cliente_blueprint.route('/avales', methods=['GET'])
def list_avales():
    def func():
        cliente_service = ClienteAvalService()
        avales = cliente_service.list_avales()
        return create_response(avales, 200)

    return handle_exceptions(func)
# List clientes para prestamo
@cliente_blueprint.route('/clientes-registro-prestamo', methods=['GET'])
def list_clientes_registro():
    def func():
        cliente_service = ClienteAvalService()
        clientes = cliente_service.list_clientes_registro()
        return create_response(clientes, 200)

    return handle_exceptions(func)


# Helpers to fill cliente
@cliente_blueprint.route('/tipos-propiedad', methods=['GET'])
def tipos_propiedad():
    def func():
        c=ClienteAvalService()
        return create_response(c.tipos_propiedad, 200)

    return handle_exceptions(func)

@cliente_blueprint.route('/estados-civiles', methods=['GET'])
def estados_civiles():
    def func():
        c=ClienteAvalService()
        return create_response(c.estados_civiles, 200)

    return handle_exceptions(func)

