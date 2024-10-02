from ..database import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    apellido_paterno = db.Column(db.String(255), nullable=False)
    apellido_materno = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    contrasena = db.Column(db.String(120), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.rol_id'))
    usuario_id_superior= db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True) #Jefe del usuario
    
    # Relationship
    rol = db.relationship('Rol', backref=db.backref('usuarios', lazy=True))

    def serialize(self):
        return {
            'userId': self.id,
            'nombre': self.nombre,
            'apellido_paterno': self.apellido_paterno,
            'apellido_materno': self.apellido_materno,
            'email': self.email,
            'rol': self.rol.nombre,
            'rol_id': self.rol_id
        }