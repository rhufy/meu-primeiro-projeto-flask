from flask import redirect, request, render_template, url_for, Blueprint, flash
from flask_login import login_user, login_required, current_user, logout_user
from usuarios_bp.database import User, Profile, Task, Critica, Comentario
from extensions import db, mail
from config import Config
from itsdangerous import URLSafeTimedSerializer
from werkzeug.utils import secure_filename
import os

usuarios_bp = Blueprint('usuarios_bp', __name__)


def get_serializer():
    return URLSafeTimedSerializer(Config.SECRET_KEY)


@usuarios_bp.route('/')
def home():
    todas_criticas = Critica.query.order_by(
        Critica.id.desc()).all()
    return render_template('home.html', criticas=todas_criticas, error_page=True)


@usuarios_bp.route('/login')
def login():
    return render_template('login.html')


@usuarios_bp.route('/autenticar', methods=['POST'])
def autenticar():
    # login_user()
    nome_usuario = request.form.get('usuario')
    # email = request.form.get('email')
    senha = request.form.get('senha')
    usuario = User.query.filter_by(nome_usuario=nome_usuario).first()
    if not usuario:
        flash('Usuario nao encontrado', 'warning')
        return redirect(url_for('usuarios_bp.login'))
    if usuario.is_locked:
        flash("Seu usuário foi bloqueado. Contate o administrador.", "danger")
        return redirect(url_for('usuarios_bp.login'))

    if not usuario.verify_password(senha):
        usuario.login_attempts += 1
        if usuario.login_attempts >= 5:
            usuario.is_locked = True
            flash("usuario bloqueado por 5 tentativas invalidas", "danger")
        else:
            flash("senha incorreta", "danger")
        db.session.commit()
        return redirect(url_for('usuarios_bp.login'))

    if usuario and usuario.verify_password(senha):
        print(f'{usuario}encontrado')
        login_user(usuario)
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('usuarios_bp.profile'))

    return redirect(url_for('usuarios_bp.login'))


@usuarios_bp.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    s = get_serializer()
    if request.method == 'POST':
        email = request.form.get('email')
        usuario = User.query.filter_by(email=email).first()
        if usuario:
            token = s.dumps(usuario.id)
            link = url_for('usuarios_bp.resetar_senha', token=token, _external=True)

            msg_body = f"Olá {usuario.nome_usuario}.clike no link para redefinir a sua senha: {link}"
            mail.send_message(subject='Redefinir Senha',
                              recipients=[email],
                              body=msg_body)
            flash('email de recuperacao enviado com sucesso', 'info')
        else:
            flash('falha no email de recuperação', 'warning')
        return redirect(url_for('usuarios_bp.login'))
    return render_template('recuperar_senha.html')


@usuarios_bp.route('/resetar_senha/<token>', methods=['GET', 'POST'])
def resetar_senha(token):
    s = get_serializer()
    try:
        user_id = s.loads(token, max_age=3600)
    except Exception:
        flash("token invalido ou expirado", "danger")
        return redirect(url_for('usuarios_bp.recuperar_senha'))
    usuario = User.query.get(user_id)
    if not usuario:
        flash("usuario n encontrado", "danger")
        return redirect(url_for("usuarios_bp.recuperar_senha"))

    if request.method == "POST":
        nova_senha = request.form.get("senha")
        if not nova_senha:
            flash("senha n pode ser vazia", "warning")
        else:
            usuario.set_password(nova_senha)
            db.session.commit()
            flash("senha redefinida com sucesso , faca login ", "success")
            return redirect(url_for("usuarios_bp.login"))
    return render_template("resetar_senha.html")


@usuarios_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome_usuario = request.form.get('usuario')
        email = request.form.get('email')
        senha = request.form.get('senha')
        # garantindo q o usario n seja none
        if not nome_usuario or not senha or not email:
            flash('usuario ou senha n existe', 'danger')
            return redirect(url_for('usuarios_bp.cadastro'))
        usuario = User.query.filter_by(nome_usuario=nome_usuario).first()

        if usuario:
            flash(f"{usuario} existe  va para a pagina de login", "info")
            return redirect(url_for('usuarios_bp.login'))

        new_usuario = User(nome_usuario=nome_usuario, email=email, senha=senha)

        db.session.add(new_usuario)
        db.session.commit()
        if new_usuario:
            login_user(new_usuario)
            flash('cadastrado com sucesso', 'success')
            return redirect(url_for('usuarios_bp.profile'))
    return render_template('cadastro.html')


@usuarios_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('logout realizado com sucesso ', 'info')
    return redirect(url_for('usuarios_bp.login'))


@usuarios_bp.route('/tarefas', methods=['GET', 'POST'])
@login_required
def tarefas():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        if titulo:
            nova_tarefa = Task(titulo=titulo, usuario=current_user)
            db.session.add(nova_tarefa)
            db.session.commit()
            flash('nova tarefa adcionada com sucesso', 'success')
            return redirect(url_for('usuarios_bp.tarefas'))
    tarefas_usuario = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('tarefas.html', tarefas=tarefas_usuario)


@usuarios_bp.route('/excluir/<int:tarefa_id>')
@login_required
def excluir(tarefa_id):
    tarefa = Task.query.filter_by(id=tarefa_id, user_id=current_user.id).first_or_404()

    db.session.delete(tarefa)
    db.session.commit()

    flash('tarefa excluida com sucesso ', 'success')

    return redirect(url_for('usuarios_bp.tarefas'))


@usuarios_bp.route('/editar/<int:tarefa_id>', methods=['GET', 'POST'])
@login_required
def editar(tarefa_id):
    tarefa = Task.query.filter_by(id=tarefa_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        novo_titulo = request.form.get('titulo')
        if novo_titulo:
            tarefa.titulo = novo_titulo
            db.session.commit()
            flash('tarefa editada com sucesso ', 'success')
            return redirect(url_for('usuarios_bp.tarefas'))
    return render_template('editar.html', tarefa=tarefa)


@usuarios_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    perfil = Profile.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        nick = request.form.get('nome')
        bio = request.form.get('conteudo')
        foto_arquivo = request.files.get('foto')

        caminho = None

        if foto_arquivo and foto_arquivo.filename != '':
            caminho = f"img/{foto_arquivo.filename}"
            foto_arquivo.save(f"static/{caminho}")

        if not nick or not bio:
            flash("preencha todos os campos", "warning")
            return redirect(url_for("usuarios_bp.profile"))

        if perfil:  # perfil já existente sendo atualizado
            perfil.nick = nick
            perfil.bio = bio
            if caminho:
                perfil.foto = caminho
            flash("perfil atualizado com sucesso", "success")
        else:
            perfil = Profile(nome=nick, bio=bio, foto=caminho, usuario=current_user)
            db.session.add(perfil)
            flash("bio criada com sucesso", "success")

        db.session.commit()
        return redirect(url_for('usuarios_bp.profile'))
    if not perfil:
        flash("Você ainda não tem um perfil. Preencha as informações abaixo para criar um.", "info")

    return render_template('profile.html', perfil=perfil, usuario=current_user)


@usuarios_bp.route('/critica/', methods=['GET', 'POST'])
def exibir_critica():
    criticas = Critica.query.all()
    critica = None

    if request.method == "POST":
        nome_jogo = request.form.get("jogo")
        if nome_jogo:
            critica = Critica.query.filter_by(jogo=nome_jogo).first()
            if not critica:
                flash("critica n encontrada", "info")
    return render_template("critica.html", criticas=criticas, critica=critica)


UPLOAD_FOLDER = 'static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@usuarios_bp.route('/criar_critica', methods=['GET', 'POST'])
def criar_critica():
    if request.method == 'POST':
        jogo = request.form['jogo']
        titulo = request.form['titulo']
        texto = request.form['texto']
        imagem = request.files['imagem']

        if imagem and allowed_file(imagem.filename):
            filename = secure_filename(imagem.filename)
            imagem.save(os.path.join(UPLOAD_FOLDER, filename))
            nova_critica = Critica(
                jogo=jogo,
                titulo=titulo,
                texto=texto,
                imagem=filename,
                user_id=current_user.id
            )

            db.session.add(nova_critica)
            db.session.commit()

            flash('Crítica criada com sucesso!', 'success')
            return redirect(url_for('usuarios_bp.criar_critica'))

        flash('Arquivo inválido. Apenas imagens são permitidas.', 'error')
        return redirect(url_for('usuarios_bp.criar_critica'))

    return render_template('critica_form.html')


@usuarios_bp.route('/critica/<int:id>')
def exibir_critica_detalhe(id):
    critica = Critica.query.get_or_404(id)
    comentarios = Comentario.query.filter_by(critica_id=id).order_by(Comentario.data_criacao.desc()).all()
    return render_template('critica_detalhe.html', critica=critica, comentarios=comentarios)


@login_required
@usuarios_bp.route('/comentario<int:id>', methods=['GET', 'POST'])
def criar_comentario(id):
    if request.method == "POST":
        comentar = request.form.get('comentario')
        if comentar and comentar.strip():
            novo_comentario = Comentario(comentario=comentar, user_id=current_user.id, critica_id=id)
            db.session.add(novo_comentario)
            db.session.commit()
            flash('Comentário criado com sucesso', 'success')
            return redirect(url_for('usuarios_bp.exibir_critica_detalhe', id=id))
        flash('comentario vazio', 'danger')
        return redirect(url_for('usuarios_bp.exibir_critica_detalhe', id=id))
    return render_template('critica_detalhe.html', id=id)
