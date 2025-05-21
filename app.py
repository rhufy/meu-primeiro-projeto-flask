from flask import Flask, redirect, render_template
from flask_migrate import Migrate
from flask_talisman import Talisman
from itsdangerous import URLSafeTimedSerializer
from extensions import db, login_manager#, mail
from usuarios_bp.routes import usuarios_bp
from usuarios_bp.database import User
from admin_bp.routes import admin_bp
from config import Config,  ProductionConfig #, TestingConfig DevelopmentConfig,  # Importando a configuração


def create_app():
    app = Flask(__name__)
    # Defina o ambiente com base em uma variável de ambiente ou use um valor padrão
    #app.config.from_object(DevelopmentConfig)  # Por padrão, usa a configuração de desenvolvimento

    # Alternativamente, você pode configurar o ambiente manualmente:
    # app.config.from_object(TestingConfig)  # Para testes
    app.config.from_object(ProductionConfig)  # Para produção
    app.config.from_object(Config)  # Carrega as configurações do arquivo config.py


    #app.config['MAIL_SUPPRESS_SEND'] = True  # evita que email real seja enviado . usar em testes ou desenvolvimento
    # Inicializando o URLSafeTimedSerializer
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    app.config['UPLOAD_FOLDER'] = 'static/img'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limita o tamanho do arquivo para 16MB

    csp = {
        'default-src': "'self'",
        'style-src': ["'self'", 'https://cdn.jsdelivr.net', 'https://fonts.googleapis.com'],
        'script-src': ["'self'", 'https://cdn.jsdelivr.net', 'https://cdnjs.cloudflare.com'],
        'font-src': ["'self'", 'https://fonts.gstatic.com'],
        'img-src': ["'self'", 'data:', 'https://exemplo.cdn.com'],  #
    }

    Talisman(app, content_security_policy=csp, force_https=True)

    db.init_app(app)
    #mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'usuarios_bp.login'

    Migrate(app, db)

    # Registra blueprints
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios_bp')
    app.register_blueprint(admin_bp, url_prefix='/admin_bp')

    # respostas de erro
    @app.errorhandler(404)
    def pagina_nao_encontrada(e):
        return render_template("errors/404.html", error_page=True), 404

    @app.errorhandler(403)
    def acesso_negado(e):
        return render_template("errors/403.html", error_page=True), 403

    @app.route('/')
    def home_redirect():
        return redirect('/usuarios_bp/')  # ou usar url_for se quiser

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # carrega um usuario do banco id


# Usando a factory pattern
if __name__ == "__main__":
    app = create_app()
    app.run()
