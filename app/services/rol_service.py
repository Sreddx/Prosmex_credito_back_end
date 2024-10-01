from app.models import Rol

from app import db

class RolService:
    def __init__(self, rol):
        if rol:
            self.rol_id = rol
    
    
    def get_rol_by_id(self):
        return Rol.query.get(self.rol_id)
    
    @staticmethod
    def get_all_roles():
        return Rol.query.all()
    
    
    