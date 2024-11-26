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
        return create_response({'message': 'Cliente created successfully', 'cliente': new_cliente.cliente_id}, 201)

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
            return create_response({'message': 'Cliente updated successfully', 'cliente': updated_cliente.cliente_id}, 200)
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
        
        # Obtén los parámetros de paginación de la solicitud
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        # Llama al servicio con los parámetros de paginación
        clientes, total_pages = cliente_service.list_clientes(page, per_page)
        
        return create_response({
            'clientes': [cliente.serialize() for cliente in clientes],
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages
        }, 200)

    return handle_exceptions(func)


# List avales para prestamo
@cliente_blueprint.route('/avales', methods=['GET'])
def list_avales():
    def func():
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        cliente_service = ClienteAvalService()
        avales, total_pages = cliente_service.list_avales(page, per_page)
        
        return create_response({
            'avales': avales,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages
        }, 200)

    return handle_exceptions(func)

# List clientes para prestamo
@cliente_blueprint.route('/clientes-registro-prestamo', methods=['GET'])
def list_clientes_registro():
    def func():
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        cliente_service = ClienteAvalService()
        clientes, total_pages = cliente_service.list_clientes_registro(page, per_page)
        
        return create_response({
            'clientes': clientes,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages
        }, 200)

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

@cliente_blueprint.route('/monto-prestado/<int:cliente_id>', methods=['GET'])
def calcular_monto_prestado(cliente_id):
    def func():
        cliente_service = ClienteAvalService(cliente_id)
        cliente = cliente_service.get_cliente()
        monto_prestado = cliente.calcular_monto_prestado()
        return create_response({'monto_prestado': monto_prestado}, 200)

    return handle_exceptions(func)

@cliente_blueprint.route('/monto-pagado/<int:cliente_id>', methods=['GET'])
def calcular_monto_pagado(cliente_id):
    def func():
        cliente_service = ClienteAvalService(cliente_id)
        cliente = cliente_service.get_cliente()
        monto_pagado = cliente.calcular_monto_pagado()
        return create_response({'monto_pagado': monto_pagado}, 200)

    return handle_exceptions(func)

@cliente_blueprint.route('/monto-restante/<int:cliente_id>', methods=['GET'])
def calcular_monto_restante(cliente_id):
    def func():
        cliente_service = ClienteAvalService(cliente_id)
        cliente = cliente_service.get_cliente()
        monto_restante = cliente.calcular_monto_restante()
        return create_response({'monto_restante': monto_restante}, 200)

    return handle_exceptions(func)

@cliente_blueprint.route('/prestamo-papel/<int:cliente_id>', methods=['GET'])
def calcular_prestamo_papel(cliente_id):
    def func():
        cliente_service = ClienteAvalService(cliente_id)
        cliente = cliente_service.get_cliente()
        prestamo_papel = cliente.calcular_prestamo_papel()
        return create_response({'prestamo_papel': prestamo_papel}, 200)

    return handle_exceptions(func)

@cliente_blueprint.route('/prestamo-real/<int:cliente_id>', methods=['GET'])
def calcular_prestamo_real(cliente_id):
    def func():
        cliente_service = ClienteAvalService(cliente_id)
        cliente = cliente_service.get_cliente()
        prestamo_real = cliente.calcular_prestamo_real()
        return create_response({'prestamo_real': prestamo_real}, 200)

    return handle_exceptions(func)