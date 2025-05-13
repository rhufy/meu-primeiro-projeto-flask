from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from extensions import db



# criando tabela User e metodos de verificar senha e armazenar<h2>OPÇÕES DO SITE</h2>

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome_usuario = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    perfil = db.relationship("Profile", back_populates="usuario", uselist=False)
    login_attempts = db.Column(db.Integer, default=0)  # responsavel pela contagem de tentativas
    is_locked = db.Column(db.Boolean, default=False)  # responsavel pelo bloqueio
    is_admin = db.Column(db.Boolean, default=False)  # admin
    criticas = db.relationship("Critica", back_populates="usuario")
    comentarios = db.relationship("Comentario", back_populates='usuario')
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, senha):
        return check_password_hash(self.password_hash, senha)

    def __init__(self, nome_usuario, senha, email, is_admin=False):
        self.nome_usuario = nome_usuario
        self.email = email
        self.password_hash = generate_password_hash(senha)
        self.is_admin = is_admin


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    usuario = db.relationship('User', backref='tarefas', lazy=True)


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120))
    bio = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    foto = db.Column(db.String(200))  # campo adicionado para testar o migrate
    usuario = db.relationship("User", back_populates="perfil")

class Critica(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jogo = db.Column(db.String(150), unique=True , nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    imagem = db.Column(db.String(100), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    usuario = db.relationship("User", back_populates="criticas")
    comentarios = db.relationship("Comentario", back_populates='critica')
    def __repr__(self):
        return f"<critica {self.jogo}>"


class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comentario = db.Column(db.String(200), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    #chaves estrangeiras
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    critica_id = db.Column(db.Integer, db.ForeignKey('critica.id'))
    #relaçao
    critica = db.relationship('Critica', back_populates='comentarios')
    usuario = db.relationship("User", back_populates='comentarios')
"""from extensions import db
from models import User  # ou ajuste o import conforme sua estrutura

admin = User(
    nome_usuario="admin",
    senha="admin123",  # será automaticamente criptografada
    email="admin@email.com",
    is_admin=True
)

db.session.add(admin)
db.session.commit()

"""
