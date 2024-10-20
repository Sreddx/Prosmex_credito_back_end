from app.models import Usuario
from flask_jwt_extended import get_jwt_identity
from app import db, bcrypt

class UsuarioService:
    @staticmethod
    def create_user(data):
        password = bcrypt.generate_password_hash(data['contrasena']).decode('utf-8')
        new_user = Usuario(
            nombre=data['nombre'],
            apellido_paterno=data['apellido_paterno'],
            apellido_materno=data['apellido_materno'],
            email=data['email'],
            contrasena=password,
            rol_id=data['rol_id']
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def get_all_users():
        return Usuario.query.all()

    @staticmethod
    def get_user_by_id(user_id):
        return Usuario.query.get(user_id)
    @staticmethod
    def get_user_rol_by_user_id(user_id):
        user = Usuario.query.get(user_id)
        return user.rol_id
    @staticmethod
    def get_user_by_email(email):
        return Usuario.query.filter_by(email=email).first()
    
    @staticmethod
    def get_specific_users(rol_name):
        roles = {
            "Gestor de cobranza": 1,
            "Titular": 2,
            "Supervisor": 3,
            "Gerente": 4,
            "Director": 5,
            "Admin": 6
        }
        if rol_name not in roles.keys():
            raise ValueError("Rol no encontrado")
        print(roles[rol_name])
        usuarios_con_rol = Usuario.query.filter_by(rol_id=roles[rol_name]).all()
        if not usuarios_con_rol:
            raise ValueError("No se encontraron usuarios con el rol proporcionado")
        return usuarios_con_rol

            
    @staticmethod
    def get_user_from_jwt():
        # Retrieve the JWT identity
        id_from_jwt = get_jwt_identity()
        
        # Query your database for the user
        user = Usuario.query.filter_by(id=id_from_jwt).first()

        # Check if a user was found
        if not user:
            raise Exception("User not found")

        return user
    
    @staticmethod
    def update_user(user_id, data):
        user = Usuario.query.get(user_id)
        if user:
            user.nombre = data.get('nombre', user.nombre)
            user.apellido_paterno = data.get('apellido_paterno', user.apellido_paterno)
            user.apellido_materno = data.get('apellido_materno', user.apellido_materno)
            user.email = data.get('email', user.email)
            user.rol_id = data.get('rol_id', user.rol_id)
            db.session.commit()
            return user
        return None

    @staticmethod
    def delete_user(user_id):
        user = Usuario.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False