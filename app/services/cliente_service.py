from app.models import ClienteAval
from app import db

class ClienteAvalService:
    @staticmethod
    def create_cliente(data):
        new_cliente = ClienteAval(
            nombre=data['nombre'],
            apellido_paterno=data['apellido_paterno'],
            apellido_materno=data['apellido_materno'],
            colonia=data['colonia'],
            cp=data['cp'],
            codigo_ine=data['codigo_ine'],
            estado_civil=data['estado_civil'],
            num_hijos=data['num_hijos'],
            propiedad=data['propiedad'],
            es_aval=data['es_aval'],
            grupo_id=data['grupo_id']
        )
        db.session.add(new_cliente)
        db.session.commit()
        return new_cliente
