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
    Rol
)
from app import db
from flask_jwt_extended import get_jwt_identity
from app.services.usuario_service import UsuarioService
from datetime import datetime, timedelta
import pytz

class ReporteService:
    @staticmethod
    def obtener_reporte():
        user = UsuarioService.get_user_from_jwt()
        user_role_id = user.rol_id
        
        if user_role_id == 1:
            return []

        filters = []

        if user_role_id in [5, 6]:
            pass
        elif user_role_id == 4:
            filters.append(Ruta.usuario_id_gerente == user.id)
        elif user_role_id == 3:
            filters.append(Ruta.usuario_id_supervisor == user.id)
        elif user_role_id == 2:
            filters.append(Grupo.usuario_id_titular == user.id)

        usuarios_gerente = aliased(Usuario)
        usuarios_supervisor = aliased(Usuario)
        usuarios_titular = aliased(Usuario)

        mexico_city_tz = pytz.timezone('America/Mexico_City')
        current_date = datetime.now(mexico_city_tz).date()
        start_of_week = current_date - timedelta(days=current_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        # Subconsulta para pagos por grupo
        pagos_por_grupo = (
            db.session.query(
                Grupo.grupo_id.label('grupo_id'),
                func.sum(Pago.monto_pagado).label('total_pagos')
            )
            .join(ClienteAval, ClienteAval.grupo_id == Grupo.grupo_id)
            .join(Prestamo, Prestamo.cliente_id == ClienteAval.cliente_id)
            .join(Pago, Pago.prestamo_id == Prestamo.prestamo_id)
            .filter(
                and_(
                    Pago.fecha_pago >= start_of_week,
                    Pago.fecha_pago <= end_of_week
                )
            )
            .group_by(Grupo.grupo_id)
        ).subquery()

        # Calcular cobranza_ideal
        cobranza_ideal_case = Prestamo.monto_prestamo * TipoPrestamo.porcentaje_semanal

        query = db.session.query(
            Grupo.grupo_id,
            Ruta.ruta_id,
            func.coalesce(func.concat(usuarios_gerente.nombre, ' ', usuarios_gerente.apellido_paterno), '').label('gerente'),
            func.coalesce(func.concat(usuarios_supervisor.nombre, ' ', usuarios_supervisor.apellido_paterno), '').label('supervisor'),
            func.coalesce(func.concat(usuarios_titular.nombre, ' ', usuarios_titular.apellido_paterno), '').label('titular'),
            Ruta.nombre_ruta.label('ruta'),
            Grupo.nombre_grupo.label('grupo'),
            func.coalesce(func.sum(cobranza_ideal_case.distinct()), 0).label('cobranza_ideal'),
            func.coalesce(pagos_por_grupo.c.total_pagos, 0).label('cobranza_real'),
            func.coalesce(func.sum(Prestamo.monto_prestamo), 0).label('prestamo_real'),
            (func.coalesce(func.sum(Prestamo.monto_prestamo.distinct()), 0) - 
             func.coalesce(func.sum(Pago.monto_pagado.distinct()), 0)).label('prestamo_papel'),
            func.count(func.distinct(Prestamo.prestamo_id)).label('numero_de_prestamos')
        ).select_from(Grupo)

        # Joins
        query = query.outerjoin(Ruta, Grupo.ruta_id == Ruta.ruta_id)
        query = query.outerjoin(usuarios_supervisor, Ruta.usuario_id_supervisor == usuarios_supervisor.id)
        query = query.outerjoin(usuarios_gerente, Ruta.usuario_id_gerente == usuarios_gerente.id)
        query = query.outerjoin(usuarios_titular, Grupo.usuario_id_titular == usuarios_titular.id)
        query = query.outerjoin(ClienteAval, ClienteAval.grupo_id == Grupo.grupo_id)
        query = query.outerjoin(Prestamo, Prestamo.cliente_id == ClienteAval.cliente_id)
        query = query.outerjoin(TipoPrestamo, Prestamo.tipo_prestamo_id == TipoPrestamo.tipo_prestamo_id)
        query = query.outerjoin(Pago, Pago.prestamo_id == Prestamo.prestamo_id)
        query = query.outerjoin(pagos_por_grupo, pagos_por_grupo.c.grupo_id == Grupo.grupo_id)

        if filters:
            query = query.filter(*filters)

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
            Grupo.nombre_grupo,
            pagos_por_grupo.c.total_pagos
        )

        results = query.all()

        # Agregar debug para verificar los pagos
        print("\nDebug - Pagos por grupo:")
        debug_query = db.session.query(
            Grupo.grupo_id,
            func.sum(Pago.monto_pagado).label('total_pagos')
        ).join(ClienteAval, ClienteAval.grupo_id == Grupo.grupo_id)\
         .join(Prestamo, Prestamo.cliente_id == ClienteAval.cliente_id)\
         .join(Pago, Pago.prestamo_id == Prestamo.prestamo_id)\
         .filter(
            and_(
                Pago.fecha_pago >= start_of_week,
                Pago.fecha_pago <= end_of_week
            )
        ).group_by(Grupo.grupo_id)
        
        for row in debug_query.all():
            print(f"Grupo {row.grupo_id}: {row.total_pagos}")

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