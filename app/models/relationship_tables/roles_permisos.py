from ...database import db

class RolesPermisos(db.Model):
    __tablename__ = 'roles_permisos'
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.rol_id'), primary_key=True)
    permiso_id = db.Column(db.Integer, db.ForeignKey('permisos.id'), primary_key=True) 
