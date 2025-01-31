import datetime
import pytz
from app.models import Pago, Prestamo, Grupo, ClienteAval, TipoPrestamo
from app import db
from sqlalchemy.orm import joinedload
from flask import current_app as app
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from app.services.falta_service import FaltaService  # Importar el servicio de faltas
from app.services.prestamo_service import PrestamoService  # Importar el servicio de préstamos
class PagoService:
    def __init__(self, pago_id=None):
        self.pago_id = pago_id

    def create_pago(self, data):
        try:
            # # Validar campos requeridos
            # required_fields = ['monto_pagado', 'prestamo_id']
            # missing_fields = [field for field in required_fields if field not in data]
            # if missing_fields:
            #     raise ValueError(f"Faltan campos requeridos: {', '.join(missing_fields)}")
            
            #print(f'Length data: {len(data)}')

            if len(data) > 1:
                lista_pagos_hechos=[]
                for pago in data:
                    # Validar prestamo al que se va a hacer el pago
                    # Asegurarse de que el préstamo exista
                    prestamo = Prestamo.query.get(pago['prestamo_id'])
                    if not prestamo:
                        raise ValueError("El préstamo especificado no existe.")
                    # Crear el pago
                    new_pago = Pago(
                        fecha_pago=pago.get('fecha_pago', datetime.datetime.now(pytz.timezone('America/Mexico_City'))),
                        monto_pagado=pago['monto_pagado'],
                        prestamo_id=pago['prestamo_id']
                    )
                    db.session.add(new_pago)
                    db.session.commit()

                    # Verificar si el préstamo se ha completado
                    prestamo.verificar_completado()
                    
                    if prestamo.verificar_pago_cubre_cobranza_ideal(new_pago):
                        print("Pago cubre cobranza ideal")
                        prestamo.actualizar_semana_activa(True)
                    else:
                        print(f'Falta registrada para el préstamo {prestamo.prestamo_id}')
                    lista_pagos_hechos.append(new_pago)
                return lista_pagos_hechos
            # Asegurarse de que el préstamo exista
            else:
                data = data[0]
                prestamo = Prestamo.query.get(data['prestamo_id'])
                if not prestamo:
                    raise ValueError("El préstamo especificado no existe.")

                # Crear el pago
                new_pago = Pago(
                    fecha_pago=data.get('fecha_pago', datetime.datetime.now(pytz.timezone('America/Mexico_City'))),
                    monto_pagado=data['monto_pagado'],
                    prestamo_id=data['prestamo_id']
                )
                db.session.add(new_pago)
                db.session.commit()

                # Verificar si el préstamo se ha completado
                prestamo.verificar_completado()
                
                if prestamo.verificar_pago_cubre_cobranza_ideal(new_pago):
                    print("Pago cubre cobranza ideal")
                    prestamo.actualizar_semana_activa(True)
                else:
                    print(f'Falta registrada para el préstamo {prestamo.prestamo_id}')
                
                return new_pago
        except (ValueError, SQLAlchemyError) as e:
            db.session.rollback()
            app.logger.error(f"Error creando pago: {str(e)}")
            raise

    def get_pago(self):
        if not self.pago_id:
            raise ValueError("Pago ID no proporcionado.")

        try:
            pago = Pago.query.get(self.pago_id)
            if not pago:
                raise ValueError(f"No se encontró el pago con ID: {self.pago_id}")
            return pago
        except SQLAlchemyError as e:
            app.logger.error(f"Error obteniendo pago: {str(e)}")
            raise ValueError("No se pudo obtener el pago.")

    def update_pago(self, data):
        pago = self.get_pago()
        if not pago:
            return None

        try:
            # Only update monto_pagado and prestamo_id, fecha_pago remains the same or updated with current time
            pago.monto_pagado = data.get('monto_pagado', pago.monto_pagado)
            pago.prestamo_id = data.get('prestamo_id', pago.prestamo_id)
            pago.fecha_pago = datetime.datetime.now(pytz.timezone('America/Mexico_City'))  # Update to current date/time
            db.session.commit()
            return pago
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error actualizando pago: {str(e)}")
            raise ValueError("No se pudo actualizar el pago.")

    def delete_pago(self):
        pago = self.get_pago()
        if not pago:
            raise ValueError(f"No se encontró el pago con ID: {self.pago_id}")

        try:
            db.session.delete(pago)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error eliminando pago: {str(e)}")
            raise ValueError("No se pudo eliminar el pago.")

    def list_pagos(self):
        try:
            pagos = Pago.query.all()
            pagos_list = [pago.serialize() for pago in pagos]
            return pagos_list
        except SQLAlchemyError as e:
            app.logger.error(f"Error listando pagos: {str(e)}")
            raise ValueError("No se pudo obtener la lista de pagos.")

    @staticmethod
    def get_grupos():
        try:
            grupos = Grupo.query.all()
            grupos_list = [{'id': grupo.grupo_id, 'nombre': grupo.nombre_grupo} for grupo in grupos]
            return grupos_list
        except SQLAlchemyError as e:
            app.logger.error(f"Error obteniendo grupos: {str(e)}")
            raise ValueError("No se pudo obtener la lista de grupos.")

    @staticmethod
    def get_prestamos_by_grupo(grupo_id):
        try:
            clientes_en_grupo = ClienteAval.query.filter_by(grupo_id=grupo_id).all()
            id_titulares = [cliente.cliente_id for cliente in clientes_en_grupo]

            prestamos_cliente = Prestamo.query.filter(Prestamo.cliente_id.in_(id_titulares)).all()
            prestamos_list = []
            for prestamo in prestamos_cliente:
                titular = prestamo.titular  # Usando la relación actualizada
                prestamos_list.append({
                    'id': prestamo.prestamo_id,
                    'monto': float(prestamo.monto_prestamo),
                    'cliente_nombrecompleto': titular.getNombreCompleto()
                })

            print(prestamos_list)
            return prestamos_list
        except SQLAlchemyError as e:
            app.logger.error(f"Error obteniendo préstamos: {str(e)}")
            raise ValueError("No se pudo obtener la lista de préstamos.")

    @staticmethod
    def get_prestamos_by_grupo_tabla(grupo_id, page=1, per_page=10):
        try:
            grupo = Grupo.query.get(grupo_id)
            if not grupo:
                raise ValueError(f"No se encontró el grupo con ID: {grupo_id}")

            titulares_en_grupo = ClienteAval.query.filter_by(grupo_id=grupo_id).all()
            id_titulares = [titular.cliente_id for titular in titulares_en_grupo]

            prestamos_cliente_query = Prestamo.query.options(
                joinedload(Prestamo.titular),
                joinedload(Prestamo.tipo_prestamo),
                joinedload(Prestamo.pagos)
            ).filter(Prestamo.cliente_id.in_(id_titulares), Prestamo.completado == False)

            total_items = prestamos_cliente_query.count()
            prestamos_cliente = prestamos_cliente_query.limit(per_page).offset((page - 1) * per_page).all()

            prestamos_list = []
            for prestamo in prestamos_cliente:
                titular = prestamo.titular
                tipo_prestamo = prestamo.tipo_prestamo
                
                # Datos nuevos
                semanas_completadas = prestamo.semana_activa
                
                # Calcular cobranza ideal
                cobranza_ideal_prestamo = prestamo.calcular_cobranza_ideal()
                pagos_validos = len([pago for pago in prestamo.pagos if pago.monto_pagado >= cobranza_ideal_prestamo])
                
                
                semanas_que_debe = tipo_prestamo.numero_semanas  # Inicialmente igual al número de semanas
                faltas = 0

                # Obtener las faltas registradas para el préstamo
                faltas_registradas = FaltaService.get_faltas_by_prestamo_id(prestamo.prestamo_id)
                faltas += len(faltas_registradas)

                # Calcular semanas que debe sumando las faltas
                semanas_que_debe = semanas_que_debe - semanas_completadas + faltas  # Número de semanas originales más faltas, menos pagos completados
                
                prestamos_list.append({
                    'GRUPO': grupo.nombre_grupo,
                    'CLIENTE': titular.getNombreCompleto(),
                    'AVAL': prestamo.aval.getNombreCompleto(),
                    'MONTO_PRÉSTAMO': float(prestamo.monto_prestamo),
                    'MONTO_PRÉSTAMO_REAL' : float(prestamo.monto_prestamo_real) if prestamo.monto_prestamo_real else float(prestamo.monto_prestamo),
                    'FECHA_PRÉSTAMO': prestamo.fecha_inicio.strftime('%Y-%m-%d'),
                    'COBRANZA_IDEAL_SEMANAL': cobranza_ideal_prestamo,
                    'TIPO_PRESTAMO': prestamo.tipo_prestamo.nombre,
                    'NUMERO_PAGOS': semanas_completadas,
                    'SEMANAS_QUE_DEBE': semanas_que_debe,
                    'PRESTAMO_ID': prestamo.prestamo_id,
                    'MONTO_UTILIDAD': float(prestamo.monto_utilidad),
                    'RENOVACION': prestamo.renovacion,
                    'COMPLETADO': prestamo.completado,
                    'MONTO_PAGADO': float(prestamo.calcular_monto_pagado()),
                })

            #prestamos_list = sorted(prestamos_list, key=lambda x: x['FECHA_PRÉSTAMO'])  # Ordenar por fecha_inicio            
            for prestamo in prestamos_list:
                print(prestamo['FECHA_PRÉSTAMO'])

            total_pages = (total_items + per_page - 1) // per_page

            return {
                'prestamos': prestamos_list,
                'page': page,
                'per_page': per_page,
                'total_items': total_items,
                'total_pages': total_pages
            }
        except SQLAlchemyError as e:
            app.logger.error(f"Error obteniendo préstamos: {str(e)}")
            raise ValueError("No se pudo obtener la lista de préstamos.")





    @staticmethod
    def get_pagos_by_prestamo_tabla(prestamo_id):
        try:
            # Obtener el préstamo con el titular y su grupo
            prestamo = Prestamo.query.options(
                joinedload(Prestamo.titular).joinedload(ClienteAval.grupo)
            ).get(prestamo_id)
            if not prestamo:
                raise ValueError(f"No se encontró el préstamo con ID: {prestamo_id}")

            cliente = prestamo.titular  # Instancia de ClienteAval
            grupo_id = cliente.grupo_id
            grupo = Grupo.query.get(grupo_id)
            if not grupo:
                raise ValueError(f"No se encontró el grupo para el cliente con ID: {cliente.cliente_id}")

            # Obtener los pagos del préstamo
            pagos = prestamo.pagos  # Lista de instancias de Pago

            # Construir la lista de pagos con la información requerida
            pagos_list = []
            for pago in pagos:
                pagos_list.append({
                    'GRUPO': grupo.nombre_grupo,
                    'CLIENTE': cliente.getNombreCompleto(),
                    'MONTO_PRESTAMO': float(prestamo.monto_prestamo),
                    'MONTO_PAGO': float(pago.monto_pagado),
                    'FECHA_PAGO': pago.fecha_pago.strftime('%Y-%m-%d')
                })

            return pagos_list
        except SQLAlchemyError as e:
            app.logger.error(f"Error obteniendo pagos: {str(e)}")
            raise ValueError("No se pudo obtener la lista de pagos.")


    @staticmethod
    def get_pagos_by_prestamo(prestamo_id):
        try:
            pagos = Pago.query.filter_by(prestamo_id=prestamo_id).all()
            pagos_list = [pago.serialize() for pago in pagos]
            return pagos_list
        except SQLAlchemyError as e:
            app.logger.error(f"Error obteniendo pagos: {str(e)}")
            raise ValueError("No se pudo obtener la lista de pagos.")
