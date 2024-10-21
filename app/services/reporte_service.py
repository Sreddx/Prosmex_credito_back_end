# app/services/reporte_service.py

from sqlalchemy import func, case, and_, text
from sqlalchemy.orm import aliased
from app.models import (
    Grupo,
    Ruta,
    Usuario,
    ClienteAval,
    Prestamo,
    TipoPrestamo,
    Pago,
    Rol  # Asegúrate de importar el modelo Rol si lo necesitas
)
from app import db
from flask_jwt_extended import get_jwt_identity
from app.services.usuario_service import UsuarioService

class ReporteService:
    @staticmethod
    def obtener_reporte():
        # Obtener el usuario actual
        user = UsuarioService.get_user_from_jwt()
        user_role_id = user.rol_id  # Obtener el ID del rol

        # Si el usuario es 'Gestor de cobranza' (rol_id = 1), devuelve una lista vacía
        if user_role_id == 1:
            return []

        # Inicializar filtros
        filters = []

        # Aplicar filtros basados en el rol
        if user_role_id in [5, 6]:  # Director (5) y Admin (6)
            # No se aplican filtros adicionales
            pass
        elif user_role_id == 4:  # Gerente
            # Filtrar por rutas asignadas al gerente
            filters.append(Ruta.usuario_id_gerente == user.id)
        elif user_role_id == 3:  # Supervisor
            # Filtrar por rutas asignadas al supervisor
            filters.append(Ruta.usuario_id_supervisor == user.id)
        elif user_role_id == 2:  # Titular
            # Filtrar por grupos asignados al titular
            filters.append(Grupo.usuario_id_titular == user.id)

        # Aliases para distinguir entre gerente, supervisor y titular
        usuarios_gerente = aliased(Usuario)
        usuarios_supervisor = aliased(Usuario)
        usuarios_titular = aliased(Usuario)

        # Inicio de la semana actual (lunes)
        current_date = func.current_date()
        start_of_week = func.date_trunc('week', current_date)

        # Calcular la fecha ajustada sumando semanas a fecha_inicio
        adjusted_date = Prestamo.fecha_inicio + (TipoPrestamo.numero_semanas * text("interval '1 week'"))

        # Subconsulta para calcular cobranza_ideal
        cobranza_ideal_case = case(
            (
                adjusted_date > current_date,
                Prestamo.monto_prestamo / TipoPrestamo.numero_semanas
            ),
            else_=0
        )

        # Subconsulta para calcular cobranza_real dentro de la semana actual
        cobranza_real_case = case(
            (
                and_(
                    Pago.fecha_pago >= start_of_week,
                    Pago.fecha_pago <= current_date
                ),
                Pago.monto_pagado
            ),
            else_=0
        )

        # Construir la consulta
        query = db.session.query(
            Grupo.grupo_id,
            Ruta.ruta_id,
            func.coalesce(func.concat(usuarios_gerente.nombre, ' ', usuarios_gerente.apellido_paterno), '').label('gerente'),
            func.coalesce(func.concat(usuarios_supervisor.nombre, ' ', usuarios_supervisor.apellido_paterno), '').label('supervisor'),
            func.coalesce(func.concat(usuarios_titular.nombre, ' ', usuarios_titular.apellido_paterno), '').label('titular'),
            Ruta.nombre_ruta.label('ruta'),
            Grupo.nombre_grupo.label('grupo'),
            func.coalesce(func.sum(cobranza_ideal_case.distinct()), 0).label('cobranza_ideal'),
            func.coalesce(func.sum(cobranza_real_case.distinct()), 0).label('cobranza_real'),
            func.coalesce(func.sum(Prestamo.monto_prestamo.distinct()), 0).label('prestamo_real'),
            (func.coalesce(func.sum(Prestamo.monto_prestamo.distinct()), 0) - func.coalesce(func.sum(Pago.monto_pagado.distinct()), 0)).label('prestamo_papel'),
            func.count(func.distinct(Prestamo.prestamo_id)).label('numero_de_prestamos')
        ).select_from(Grupo)

        # Joins
        query = query.outerjoin(Ruta, Grupo.ruta_id == Ruta.ruta_id)
        query = query.outerjoin(usuarios_supervisor, Ruta.usuario_id_supervisor == usuarios_supervisor.id)
        query = query.outerjoin(usuarios_gerente, Ruta.usuario_id_gerente == usuarios_gerente.id)
        query = query.outerjoin(usuarios_titular, Grupo.usuario_id_titular == usuarios_titular.id)
        query = query.outerjoin(ClienteAval, ClienteAval.grupo_id == Grupo.grupo_id)
        query = query.outerjoin(Prestamo, Prestamo.cliente_id == ClienteAval.titular_id)
        query = query.outerjoin(TipoPrestamo, Prestamo.tipo_prestamo_id == TipoPrestamo.tipo_prestamo_id)
        query = query.outerjoin(Pago, Pago.prestamo_id == Prestamo.prestamo_id)

        # Aplicar filtros
        if filters:
            query = query.filter(*filters)

        # Agrupar
        query = query.group_by(
            Grupo.grupo_id,
            Ruta.ruta_id,
            usuarios_gerente.nombre,
            usuarios_gerente.apellido_paterno,
            usuarios_supervisor.nombre,
            usuarios_supervisor.apellido_paterno,
            usuarios_titular.nombre,
            usuarios_titular.apellido_paterno,
            Ruta.nombre_ruta,
            Grupo.nombre_grupo
        )

        # Ejecutar la consulta y obtener resultados
        results = query.all()

        # Preparar los datos finales
        report_data = []
        for row in results:
            cobranza_ideal = float(row.cobranza_ideal or 0)
            cobranza_real = float(row.cobranza_real or 0)
            prestamo_real = float(row.prestamo_real or 0)
            prestamo_papel = float(row.prestamo_papel or 0)
            numero_de_prestamos = row.numero_de_prestamos or 0

            morosidad_monto = cobranza_ideal - cobranza_real
            morosidad_porcentaje = None
            if cobranza_ideal != 0:
                morosidad_porcentaje = morosidad_monto / cobranza_ideal

            porcentaje_prestamo = None
            if prestamo_real != 0:
                porcentaje_prestamo = cobranza_real / prestamo_real

            sobrante = cobranza_real - prestamo_real

            report_data.append({
                'grupo_id': row.grupo_id,
                'gerente': row.gerente if row.gerente else None,
                'supervisor': row.supervisor if row.supervisor else None,
                'titular': row.titular if row.titular else None,
                'ruta': row.ruta if row.ruta else None,
                'grupo': row.grupo if row.grupo else None,
                'cobranza_ideal': cobranza_ideal,
                'cobranza_real': cobranza_real,
                'prestamo_papel': prestamo_papel,
                'prestamo_real': prestamo_real,
                'numero_de_prestamos': numero_de_prestamos,
                'morosidad_monto': morosidad_monto,
                'morosidad_porcentaje': morosidad_porcentaje,
                'porcentaje_prestamo': porcentaje_prestamo,
                'sobrante': sobrante
            })

        return report_data


