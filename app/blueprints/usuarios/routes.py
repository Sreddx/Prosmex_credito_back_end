from flask import Blueprint, request, jsonify
from app.services import UsuarioService
from ..helpers import *
user_blueprint = Blueprint('user', __name__, url_prefix='/users')



@user_blueprint.route('/', methods=['GET'])
def get_all_users():
    users = UsuarioService.get_all_users()
    if len(users) == 0:
        return make_response({'message': 'No users found'}, 404)
    users = [user.serialize() for user in users]
    return make_response(users, 200)

@user_blueprint.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = UsuarioService.get_user_by_id(user_id)
    if user:
        return jsonify({'id': user.id, 'nombre': user.nombre, 'email': user.email})
    return jsonify({'message': 'User not found'}), 404

@user_blueprint.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    updated_user = UsuarioService.update_user(user_id, data)
    if updated_user:
        return jsonify({'message': 'User updated successfully'})
    return jsonify({'message': 'User not found'}), 404

@user_blueprint.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if UsuarioService.delete_user(user_id):
        return jsonify({'message': 'User deleted successfully'})
    return jsonify({'message': 'User not found'}), 404
