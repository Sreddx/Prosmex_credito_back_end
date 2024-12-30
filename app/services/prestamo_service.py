from app.models import Prestamo, TipoPrestamo
from app.models.cliente_aval import ClienteAval
from app.services import usuario_service
from app import db
from flask import current_app as app
from sqlalchemy.exc import SQLAlchemyError
from app.constants import TIMEZONE
from datetime import datetime
from app.services.falta_service import FaltaService  # Importar el servicio de faltas

class PrestamoService:
    def __init__(self, prestamo_id=None):
        self.prestamo_id = prestamo_id
   
    @staticmethod
    def __check_override_monto_prestamo(monto_prestamo, user):
        user_role = usuario_service.UsuarioService.get_user_rol_by_user_id(user.id)
        if monto_prestamo<=5000:
            return True
        elif monto_prestamo>=5000 and user_role == 6:
            return True
        else:
            return False
            
    @staticmethod
    def calcular_utilidad(monto_prestamo, tipo_prestamo):
        return (monto_prestamo * tipo_prestamo.interes) + monto_prestamo

    # Método para crear un nuevo préstamo
    def create_prestamo(self, data, user):
        monto_prestamo = data['monto_prestamo']
        if self.__check_override_monto_prestamo(monto_prestamo, user):
            try:
                fecha_inicio = data.get('fecha_inicio', datetime.now(TIMEZONE))

                # Obtén el tipo de préstamo para calcular el porcentaje semanal y el número de semanas
                tipo_prestamo = TipoPrestamo.query.get(data['tipo_prestamo_id'])
                if not tipo_prestamo:
                    raise ValueError("Tipo de préstamo no encontrado.")

                # Calcula la utilidad usando el método estático
                monto_utilidad = self.calcular_utilidad(monto_prestamo, tipo_prestamo)

                # Crea el nuevo préstamo con el monto de utilidad calculado
                new_prestamo = Prestamo(
                    cliente_id=data['cliente_id'],
                    fecha_inicio=fecha_inicio,
                    monto_prestamo=monto_prestamo,
                    monto_utilidad=monto_utilidad,
                    tipo_prestamo_id=data['tipo_prestamo_id'],
                    aval_id=data['aval_id']
                )
                db.session.add(new_prestamo)
                db.session.commit()
                return new_prestamo
            except SQLAlchemyError as e:
                db.session.rollback()
                app.logger.error(f"Error creando préstamo: {str(e)}")
                raise ValueError("No se pudo crear el préstamo.")
        else:
            raise ValueError("No tienes permisos para agregar un préstamo mayor a 5000.")
                

    def get_prestamo(self):
        if not self.prestamo_id:
            raise ValueError("Prestamo ID no proporcionado.")

        try:
            prestamo = Prestamo.query.get(self.prestamo_id)
            if not prestamo:
                raise ValueError(f"No se encontró el préstamo con ID: {self.prestamo_id}")
            return prestamo
        except SQLAlchemyError as e:
            app.logger.error(f"Error obteniendo préstamo: {str(e)}")
            raise ValueError("No se pudo obtener el préstamo.")

    def update_prestamo(self, data):
        prestamo = self.get_prestamo()
        if not prestamo:
            return None

        try:
            prestamo.cliente_id = data.get('cliente_id', prestamo.cliente_id)
            prestamo.fecha_inicio = data.get('fecha_inicio', prestamo.fecha_inicio)
            prestamo.monto_prestamo = data.get('monto_prestamo', prestamo.monto_prestamo)
            prestamo.tipo_prestamo_id = data.get('tipo_prestamo_id', prestamo.tipo_prestamo_id)
            prestamo.aval_id = data.get('aval_id', prestamo.aval_id)
            prestamo.completado = data.get('completado', prestamo.completado)
            prestamo.renovacion = data.get('renovacion', prestamo.renovacion)
            prestamo.semana_activa = data.get('semana_activa', prestamo.semana_activa)
            

            db.session.commit()
            return prestamo
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error actualizando préstamo: {str(e)}")
            raise ValueError("No se pudo actualizar el préstamo.")

    def delete_prestamo(self):
        prestamo = self.get_prestamo()
        if not prestamo:
            raise ValueError(f"No se encontró el préstamo con ID: {self.prestamo_id}")

        try:
            db.session.delete(prestamo)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error eliminando préstamo: {str(e)}")
            raise ValueError("No se pudo eliminar el préstamo.")

    def list_prestamos(self, page=1, per_page=10):
        try:
            pagination = Prestamo.query.paginate(page=page, per_page=per_page, error_out=False)
            lista_obj_prestamos = pagination.items
            total_pages = pagination.pages
            total_items = pagination.total

            prestamos = []
            for prestamo in lista_obj_prestamos:
                tipo_prestamo = prestamo.tipo_prestamo

                # Datos nuevos
                semanas_completadas = prestamo.semana_activa

                semanas_que_debe = tipo_prestamo.numero_semanas  # Inicialmente igual al número de semanas
                faltas = 0

                # Obtener las faltas registradas para el préstamo
                faltas_registradas = FaltaService.get_faltas_by_prestamo_id(prestamo.prestamo_id)
                faltas += len(faltas_registradas)

                # Calcular semanas que debe sumando las faltas
                semanas_que_debe = semanas_que_debe - semanas_completadas + faltas  # Número de semanas originales más faltas, menos pagos completados

                prestamos.append({
                    'prestamo_id': prestamo.prestamo_id,
                    'cliente_id': prestamo.titular.cliente_id,
                    'cliente_nombre': f"{prestamo.titular.nombre} {prestamo.titular.apellido_paterno} {prestamo.titular.apellido_materno}",
                    'fecha_inicio': prestamo.fecha_inicio.strftime('%Y-%m-%d'),
                    'monto_prestamo': float(prestamo.monto_prestamo),
                    'monto_prestamo_real': float(prestamo.monto_prestamo_real) if prestamo.monto_prestamo_real else float(prestamo.monto_prestamo),
                    'monto_utilidad': float(prestamo.monto_utilidad),
                    'monto_pagado': float(prestamo.calcular_monto_pagado()),
                    'tipo_prestamo_id': prestamo.tipo_prestamo_id,
                    'tipo_prestamo_nombre': prestamo.tipo_prestamo.nombre,
                    'aval_id': prestamo.aval.cliente_id,
                    'aval_nombre': f"{prestamo.aval.nombre} {prestamo.aval.apellido_paterno} {prestamo.aval.apellido_materno}",
                    'renovacion': prestamo.renovacion,
                    'completado': prestamo.completado,
                    'semana_activa': prestamo.semana_activa,
                    'fecha_creacion': prestamo.fecha_inicio,
                    'numero_pagos': semanas_completadas,
                    'semanas_que_debe': semanas_que_debe,
                })

            return {
                'prestamos': prestamos,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'total_items': total_items
            }
        except SQLAlchemyError as e:
            app.logger.error(f"Error listando préstamos: {str(e)}")
            raise ValueError("No se pudo obtener la lista de préstamos.")
        
    def count_prestamos_activos(self, grupo_id):
        # Dado un id de grupo, obtiene el conteo de préstamos activos (no completados) de ese grupo
        try:
            count_activos = Prestamo.query.join(ClienteAval, ClienteAval.cliente_id == Prestamo.cliente_id)\
                                        .filter(ClienteAval.grupo_id == grupo_id, Prestamo.completado == False)\
                                        .count()
            return count_activos
        except Exception as e:
            app.logger.error(f"Error contando préstamos activos: {str(e)}")
            raise ValueError("No se pudo obtener el conteo de préstamos activos.")

        
    def list_tipos_prestamo(self):
        try:
            tipos_prestamo = TipoPrestamo.query.all()
            tipos = [tipos_prestamo.serialize() for tipos_prestamo in tipos_prestamo]
            return tipos
        except SQLAlchemyError as e:
            app.logger.error(f"Error listando tipos de préstamo: {str(e)}")
            raise ValueError("No se pudo obtener la lista de tipos de préstamo.")
    
    def get_prestamo_real_y_papel_by_grupo(self, grupo_id):
        try:
            clientes_grupo = ClienteAval.query.filter_by(grupo_id=grupo_id).all()
            # Obtener todos los prestamos de cada cliente en el grupo y que esten activos
            prestamo_real_grupo = 0
            prestamo_papel_grupo = 0
            for cliente in clientes_grupo:
                prestamo_real_grupo += cliente.calcular_prestamo_real()
                prestamo_papel_grupo += cliente.calcular_prestamo_papel()
            return prestamo_real_grupo, prestamo_papel_grupo
            
                
        except SQLAlchemyError as e:
            app.logger.error(f"Error obteniendo préstamos reales y papeles por grupo: {str(e)}")
            raise ValueError("No se pudo obtener los préstamos reales por grupo.")
    
