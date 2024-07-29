from flask import Blueprint, request, jsonify
from app.services import ClienteAvalService

cliente_blueprint = Blueprint('cliente', __name__, url_prefix='/clientes')

@cliente_blueprint.route('/', methods=['POST'])
def create_cliente():
    data = request.get_json()
    new_cliente = ClienteAvalService.create_cliente(data)
    return jsonify({'message': 'Cliente created successfully', 'cliente': new_cliente.titular_id}), 201
