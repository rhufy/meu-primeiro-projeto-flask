from flask import redirect, render_template, url_for, flash, Blueprint
from flask_login import login_required, current_user
from usuarios_bp.database import User, Comentario, Critica
from extensions import db, admin_required
admin_bp = Blueprint("admin_bp",__name__)
@admin_bp.route('/bloquear/<int:user_id>')
@login_required
@admin_required
def bloquear_usuario(user_id):
    usuario = User.query.get(user_id)
    if usuario.id == current_user.id:
        flash("Você não pode bloquear a si mesmo.", "danger")
        return redirect(url_for('admin_bp.painel_admin'))
    if usuario:
        usuario.is_locked = True  # ou qualquer atributo que você use para indicar bloqueio
        db.session.commit()
        flash(f"Usuário {usuario.nome_usuario} foi bloqueado.", "success")
    else:
        flash("Usuário não encontrado.", "danger")
    return redirect(url_for('admin_bp.painel_admin'))


@admin_bp.route('/desbloquear/<int:user_id>')
@login_required
@admin_required
def desbloquear_usuario(user_id):

    usuario = User.query.get(user_id)
    if usuario:
        usuario.is_locked = False
        usuario.login_attempts = 0
        db.session.commit()
        flash(f"usuario {usuario.nome_usuario}desbloqueado com sucesso ", "success")
    else:
        flash("usuario n encotrado", "warning")
    return redirect(url_for('admin_bp.painel_admin'))





@admin_bp.route('/usuarios')
@login_required
@admin_required
def listar_usuarios():
    usuarios = User.query.all()
    return render_template("usuarios.html", usuarios=usuarios)


@admin_bp.route('/admin')
@login_required
@admin_required
def painel_admin():

    usuarios = User.query.all()
    return render_template("painel_admin.html", usuarios=usuarios)
@admin_bp.route('/excluir_critica/<int:critica_id>')
@login_required
@admin_required
def excluir_critica(critica_id):
    critica= Critica.query.get_or_404(critica_id)
    db.session.delete(critica)
    db.session.commit()
    flash('critica apagada com sucesso', 'success')
    return redirect(url_for('admin_bp.painel_admin'))
@admin_bp.route('/excluir_comentario/<int:comentario_id>')
@login_required
@admin_required
def excluir_comentario(comentario_id):
    comentario= Comentario.query.get_or_404(comentario_id)
    db.session.delete(comentario)
    db.session.commit()
    flash('Comentário apagado com sucesso', "success")
    return redirect(url_for("admin_bp.painel_admin"))

