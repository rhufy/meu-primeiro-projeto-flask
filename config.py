# config.py

import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'valor-inseguro')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

class DevelopmentConfig(Config):
    DEBUG = True
    # Banco de dados para desenvolvimento
    SQLALCHEMY_DATABASE_URI = 'sqlite:///meubanco.db'

class TestingConfig(Config):
    # Banco de dados em memória para testes (não afeta o banco de dados real)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Banco de dados temporário em memória para testes

class ProductionConfig(Config):
    DEBUG = False
    # Banco de dados para produção (use variáveis de ambiente para segurança)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL não configurado no ambiente de produção")
