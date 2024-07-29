from app.models import Rol

from app import db

class RolService:
    @staticmethod
    def get_all_roles():
        return Rol.query.all()