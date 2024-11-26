from math import ceil
from app.models import ClienteAval
from app import db
from .service_helpers import validate_key
from flask import current_app as app
from sqlalchemy.exc import SQLAlchemyError

class ClienteAvalService:
    def __init__(self, cliente_id=None):
        self.cliente_id = cliente_id
        self.tipos_propiedad = ['casa_propia', 'rentada', 'prestada']
        self.estados_civiles = ['casado', 'divorciado', 'viudo', 'soltero']
        self.parametros = ['nombre', 'apellido_paterno', 'apellido_materno', 'colonia', 'cp', 'codigo_ine', 'estado_civil', 'num_hijos', 'propiedad', 'grupo_id']
        

    def validate_data(self, data):
        if not validate_key(data, self.parametros):
            raise ValueError("Faltan campos obligatorios para crear el cliente.")
        
        if data['propiedad'] not in self.tipos_propiedad:
            raise ValueError("Tipo de propiedad no válido.")
        
        if data['estado_civil'] not in self.estados_civiles:
            raise ValueError("Estado civil no válido.")
        
        if len(data['cp']) != 5 or not data['cp'].isdigit():
            raise ValueError("Código postal no válido.")
        
        if data['num_hijos'] < 0:
            raise ValueError("El número de hijos no puede ser negativo.")

    def create_cliente(self, data):
        self.validate_data(data)
        
        try:
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
                grupo_id=data['grupo_id']
            )
            db.session.add(new_cliente)
            db.session.commit()
            return new_cliente
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error creando cliente: {str(e)}")
            raise ValueError("No se pudo crear el cliente.")

    def get_cliente(self):
        if not self.cliente_id:
            raise ValueError("Cliente ID no proporcionado.")

        try:
            cliente = ClienteAval.query.get(self.cliente_id)
            
            if not cliente:
                raise ValueError(f"No se encontró el cliente con ID: {self.cliente_id}")
            return cliente
        except SQLAlchemyError as e:
            app.logger.error(f"Error obteniendo cliente: {str(e)}")
            raise ValueError("No se pudo obtener el cliente.")

    def update_cliente(self, data):
        cliente = self.get_cliente()
        if not cliente:
            return None
        
        if 'propiedad' in data and data['propiedad'] not in self.tipos_propiedad:
            raise ValueError("Tipo de propiedad no válido.")
        
        if 'estado_civil' in data and data['estado_civil'] not in self.estados_civiles:
            raise ValueError("Estado civil no válido.")
        
        if 'cp' in data and (len(data['cp']) != 5 or not data['cp'].isdigit()):
            raise ValueError("Código postal no válido.")
        
        if 'num_hijos' in data and data['num_hijos'] < 0:
            raise ValueError("El número de hijos no puede ser negativo.")

        try:
            cliente.nombre = data.get('nombre', cliente.nombre)
            cliente.apellido_paterno = data.get('apellido_paterno', cliente.apellido_paterno)
            cliente.apellido_materno = data.get('apellido_materno', cliente.apellido_materno)
            cliente.colonia = data.get('colonia', cliente.colonia)
            cliente.cp = data.get('cp', cliente.cp)
            cliente.codigo_ine = data.get('codigo_ine', cliente.codigo_ine)
            cliente.estado_civil = data.get('estado_civil', cliente.estado_civil)
            cliente.num_hijos = data.get('num_hijos', cliente.num_hijos)
            cliente.propiedad = data.get('propiedad', cliente.propiedad)
            cliente.es_aval = data.get('es_aval', cliente.es_aval)
            cliente.grupo_id = data.get('grupo_id', cliente.grupo_id)

            db.session.commit()
            return cliente
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error actualizando cliente: {str(e)}")
            raise ValueError("No se pudo actualizar el cliente.")

    def delete_cliente(self):
        cliente = self.get_cliente()
        if not cliente:
            raise ValueError(f"No se encontró el cliente con ID: {self.cliente_id}")

        try:
            db.session.delete(cliente)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error eliminando cliente: {str(e)}")
            raise ValueError("No se pudo eliminar el cliente.")

    def list_clientes(self, page=1, per_page=10):
        try:
            # Obtén la lista de clientes con paginación
            clientes_query = ClienteAval.query.paginate(page=page, per_page=per_page, error_out=False)
            
            # Calcula el número total de páginas
            total_pages = ceil(clientes_query.total / per_page)
            
            return clientes_query.items, total_pages
        except SQLAlchemyError as e:
            app.logger.error(f"Error listando clientes: {str(e)}")
            raise ValueError("No se pudo obtener la lista de clientes.")
    
    def list_clientes_registro(self, page=1, per_page=10):
        try:
            clientes_query = ClienteAval.query.order_by(ClienteAval.nombre.asc()).paginate(page=page, per_page=per_page, error_out=False)
            clientes_list = []
            for cliente in clientes_query.items:
                clientes_list.append({
                    'id': cliente.cliente_id,
                    'nombre': f"{cliente.nombre} {cliente.apellido_paterno} {cliente.apellido_materno}",
                    'grupo_id': cliente.grupo_id
                })
            total_pages = ceil(clientes_query.total / per_page)
            return clientes_list, total_pages
        except SQLAlchemyError as e:
            app.logger.error(f"Error listando clientes: {str(e)}")
            raise ValueError("No se pudo obtener la lista de clientes.")

    def list_avales(self, page=1, per_page=10):
        try:
            clientes_avales_query = ClienteAval.query.filter_by(es_aval=True).order_by(ClienteAval.nombre.asc()).paginate(page=page, per_page=per_page, error_out=False)
            avales = []
            for aval in clientes_avales_query.items:
                avales.append({
                    'id': aval.cliente_id,
                    'nombre': f"{aval.nombre} {aval.apellido_paterno} {aval.apellido_materno}",
                    'grupo_id': aval.grupo_id
                })
            total_pages = ceil(clientes_avales_query.total / per_page)
            return avales, total_pages
        except SQLAlchemyError as e:
            app.logger.error(f"Error listando avales: {str(e)}")
            raise ValueError("No se pudo obtener la lista de avales.")