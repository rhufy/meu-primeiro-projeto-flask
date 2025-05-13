# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_mail import Mail
# admin_required
from functools import wraps
from flask import redirect, url_for, flash

#extensoes padrao
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()


# admin_required
def admin_required(f):
    @wraps(f)
    def decorador_funcao(*args,**kwargs):
        if not current_user.is_authenticated:
            flash("faça login para acessar esta pagina","warning")
            return redirect(url_for("usuarios_bp.login"))
        if not current_user.is_admin:
            flash("Acesso negado","danger")
            return redirect(url_for("usuarios_bp.profile"))
        return f(*args, **kwargs)
    return decorador_funcao
