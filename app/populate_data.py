from app.models import Accion, Permiso, Rol, Grupo, Ruta, TipoPrestamo, Usuario
from app import db

def populate_data():
    # Check if initial data exists
    if Accion.query.first() is not None:
        return "Initial data already exists."

    
    # Define acciones
    acciones = [
        'Alta de cliente/aval', 'Creación de préstamo', 'Registro de pagos de cobranzas a nivel grupo',
        'Realizar corte con superior', 'Registro pagos de préstamos a nivel grupo', 'Visualizar reportes de rutas',
        'Visualizar reportes generales', 'Editar información', 'Crear usuario', 'Dar de baja usuario',
        'Creación de préstamo mayor a $5000', 'Eliminar crédito', 'Asignar titular a grupo', 'Asignar grupo a ruta'
    ]

    # Add acciones to the database
    accion_objects = []
    for accion_desc in acciones:
        accion = Accion(descripcion=accion_desc)
        db.session.add(accion)
        accion_objects.append(accion)
    db.session.commit()

    # Define roles
    roles = [
        'Gestor de cobranza', 'Titular', 'Supervisor', 'Gerente', 'Director', 'Admin'
    ]

    # Add roles to the database
    role_objects = []
    for role_name in roles:
        role = Rol(nombre=role_name)
        db.session.add(role)
        role_objects.append(role)
    db.session.commit()

    # Assigning permissions to roles
    roles_permisos = {
        'Gestor de cobranza': [3, 4],
        'Titular': [1, 2, 3, 4],
        'Supervisor': [1, 2, 3, 4, 5, 6],
        'Gerente': [1, 2, 3, 4, 5, 6],
        'Director': [1, 2, 3, 4, 5, 6, 7],
        'Admin': list(range(1, 15))
    }

    # Create and assign permisos based on roles_permisos
    for role_name, permiso_indices in roles_permisos.items():
        role = next((r for r in role_objects if r.nombre == role_name), None)
        if role:
            for index in permiso_indices:
                accion = accion_objects[index - 1]
                permiso = Permiso(rol_id=role.rol_id, accion_id=accion.accion_id)
                db.session.add(permiso)
    db.session.commit()

    # Create dummy data for Rutas
    rutas = [
        {'nombre_ruta': 'Ruta 1'},
        {'nombre_ruta': 'Ruta 2'},
        {'nombre_ruta': 'Ruta 3'}
    ]

    ruta_objects = []
    for ruta in rutas:
        new_ruta = Ruta(nombre_ruta=ruta['nombre_ruta'])
        db.session.add(new_ruta)
        ruta_objects.append(new_ruta)
    db.session.commit()

    # Create a dummy user to serve as group leader
    
    leader_user = Usuario(
        nombre="Leader",
        apellido_paterno="User",
        apellido_materno="One",
        email="leader.user@example.com",
        contrasena="leader123",
        rol_id=1  # Assuming the role ID 1 exists
    )
    db.session.add(leader_user)
    db.session.commit()

    # Create dummy data for Grupos
    grupos = [
        {'nombre_grupo': 'Grupo 1', 'ruta_id': ruta_objects[0].ruta_id},
        {'nombre_grupo': 'Grupo 2', 'ruta_id': ruta_objects[1].ruta_id},
        {'nombre_grupo': 'Grupo 3', 'ruta_id': ruta_objects[2].ruta_id}
    ]

    for grupo in grupos:
        new_grupo = Grupo(
            nombre_grupo=grupo['nombre_grupo'],
            ruta_id=grupo['ruta_id'],
            usuario_id_lider=leader_user.id  # Using the leader user's ID
        )
        db.session.add(new_grupo)
    db.session.commit()

    # Create dummy data for TiposPrestamo
    tipos_prestamo = [
        {
            'nombre': 'Préstamo Personal',
            'numero_semanas': 24,
            'porcentaje_semanal': 1.5,
            'incumplimientos_tolerados': 2,
            'pena_incumplimiento': 100.0,
            'limite_penalizaciones': 5
        },
        {
            'nombre': 'Préstamo Hipotecario',
            'numero_semanas': 360,
            'porcentaje_semanal': 0.5,
            'incumplimientos_tolerados': 3,
            'pena_incumplimiento': 500.0,
            'limite_penalizaciones': 10
        },
        {
            'nombre': 'Préstamo Automotriz',
            'numero_semanas': 60,
            'porcentaje_semanal': 1.0,
            'incumplimientos_tolerados': 1,
            'pena_incumplimiento': 200.0,
            'limite_penalizaciones': 7
        }
    ]

    for tipo in tipos_prestamo:
        new_tipo = TipoPrestamo(
            nombre=tipo['nombre'],
            numero_semanas=tipo['numero_semanas'],
            porcentaje_semanal=tipo['porcentaje_semanal'],
            incumplimientos_tolerados=tipo['incumplimientos_tolerados'],
            pena_incumplimiento=tipo['pena_incumplimiento'],
            limite_penalizaciones=tipo['limite_penalizaciones']
        )
        db.session.add(new_tipo)
    db.session.commit()
