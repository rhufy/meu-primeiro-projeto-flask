# config.py

import os

class Config:
    SECRET_KEY = '1234'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'seuemail@gmail.com'
    MAIL_PASSWORD = 'suasenhaouappkey'
    MAIL_DEFAULT_SENDER = 'seuemail@gmail.com'

class DevelopmentConfig(Config):
    # Banco de dados para desenvolvimento
    SQLALCHEMY_DATABASE_URI = 'sqlite:///meubanco.db'

class TestingConfig(Config):
    # Banco de dados em memória para testes (não afeta o banco de dados real)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Banco de dados temporário em memória para testes

class ProductionConfig(Config):
    # Banco de dados para produção (use variáveis de ambiente para segurança)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///meubanco.db')
