import sys
import os
import io
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from app import create_app
from usuarios_bp.database import User, Task, Profile
from extensions import db
from usuarios_bp.routes import get_serializer

@pytest.fixture
def client():
    # setup
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Banco de dados em memória para testes
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAIL_SUPPRESS_SEND'] = True
    # teardown
    with app.app_context():
        db.create_all()  # Cria as tabelas no banco de dados

        yield app.test_client()  # Retorna o client de teste para os testes

        db.session.remove()
        db.drop_all()  # Depois do teste, remove todas as tabelas


def test_login_with_email(client):
    user = User(nome_usuario='user_email', senha='senha123', email='user@email.com')
    db.session.add(user)
    db.session.commit()

    response = client.post('/usuarios_bp/autenticar', data={'usuario': 'user_email', 'senha': 'senha123'},
                           follow_redirects=True)
    assert response.status_code == 200
    assert b'Login realizado com sucesso!' in response.data


def test_login_with_username(client):
    user = User(nome_usuario='user_name', senha='senha456', email='user2@email.com')
    db.session.add(user)
    db.session.commit()

    response = client.post('/usuarios_bp/autenticar', data={'usuario': 'user_name', 'senha': 'senha456'},
                           follow_redirects=True)
    assert response.status_code == 200
    assert b'Login realizado com sucesso!' in response.data


def test_cadastro(client):
    # criação do usuario

    # requerimento e redirect apos fomulario posto
    response = client.post('/usuarios_bp/cadastro',
                           data={'usuario': 'user_name1', 'email': 'user3@email.com', 'senha': 'senha456'},
                           follow_redirects=True)

    print(response.data)
    # assertamento
    assert response.status_code == 200
    assert b'cadastrado com sucesso' in response.data
    # verifica se o usuario foi realmente colocado e salvo no banco de dados
    user = User.query.filter_by(nome_usuario='user_name1').first()
    assert user is not None


def test_cadastro_exist(client):
    # primeiro cadastro
    client.post('/usuarios_bp/cadastro',
                data={'usuario': 'user_name1', 'email': 'user3@email.com', 'senha': 'senha456'},
                follow_redirects=True)
    # tenta cadastrar dnv
    response = client.post('/usuarios_bp/cadastro',
                           data={'usuario': 'user_name1', 'email': 'user3@email.com', 'senha': 'senha456'},
                           follow_redirects=True)

    assert response.status_code == 200
    # n usei o {usuario} pq o assert n aceita , mas o resto do texto ttem que tar igual
    assert b' existe  va para a pagina de login' in response.data


def test_cadastro_not_dados(client):
    # vou testar a mensagem de  sem dados , para isso eu tirei o user name
    response = client.post('/usuarios_bp/cadastro',
                           data={'usuario': '', 'email': 'user3@email.com', 'senha': 'senha456'},
                           follow_redirects=True)
    assert response.status_code == 200
    assert b'usuario ou senha n existe' in response.data


# teste de funcionalidades em login
def test_tarefas(client):  # aqui eu vejo e crio tarefas
    # criando um login
    user = User(nome_usuario='user_name', senha='senha456', email='user2@email.com')
    db.session.add(user)
    db.session.commit()
    client.post('/usuarios_bp/autenticar', data={'usuario': 'user_name', 'senha': 'senha456'},
                follow_redirects=True)
    # testando a rota tarefas
    response = client.post('/usuarios_bp/tarefas', data={'titulo': 'titulo'}, follow_redirects=True)
    tarefas = Task.query.filter_by(user_id=user.id).all()

    assert response.status_code == 200
    assert tarefas is not None
    assert len(tarefas) == 1
    assert tarefas[0].titulo == 'titulo'


def test_tarefas_semdados(client):
    # criando um login
    user = User(nome_usuario='user_name', senha='senha456', email='user2@email.com')
    db.session.add(user)
    db.session.commit()
    client.post('/usuarios_bp/autenticar', data={'usuario': 'user_name', 'senha': 'senha456'},
                follow_redirects=True)
    # testando a rota tarefas
    response = client.post('/usuarios_bp/tarefas', data={'titulo': ''}, follow_redirects=True)

    assert response.status_code == 200
    assert Task.query.filter_by(user_id=user.id).count() == 0  # nenhuma tarefa deve ser criada


def test_terafas_excluir(client):
    # criando um login
    user = User(nome_usuario='user_name', senha='senha456', email='user2@email.com')
    db.session.add(user)
    db.session.commit()
    client.post('/usuarios_bp/autenticar', data={'usuario': 'user_name', 'senha': 'senha456'},
                follow_redirects=True)

    # criando a tarefa que sera testada e exclusao
    response = client.post('/usuarios_bp/tarefas', data={'titulo': 'tarefa_excluida'}, follow_redirects=True)

    # apagando a tarefa
    tarefa = Task.query.filter_by(user_id=user.id, titulo='tarefa_excluida').first()
    response = client.get(f'/usuarios_bp/excluir/{tarefa.id}', follow_redirects=True)
    # testes
    assert response.status_code == 200
    assert Task.query.filter_by(id=tarefa.id).first() is None


def test_editar_tarefas(client):
    # criando um login
    user = User(nome_usuario='user_name', senha='senha456', email='user2@email.com')
    db.session.add(user)
    db.session.commit()
    client.post('/usuarios_bp/autenticar', data={'usuario': 'user_name', 'senha': 'senha456'},
                follow_redirects=True)

    # criando a tarefa que sera testada e edição
    response = client.post('/usuarios_bp/tarefas', data={'titulo': 'tarefa_editar'}, follow_redirects=True)

    # criando a ediçao
    tarefa = Task.query.filter_by(user_id=user.id, titulo='tarefa_editar').first()
    response = client.post(f'/usuarios_bp/editar/{tarefa.id}', data={'titulo': 'tarefa_editada'}, follow_redirects=True)
    tarefa_editada = db.session.get(Task, tarefa.id)
    assert response.status_code == 200
    assert tarefa_editada is not None
    assert tarefa_editada.titulo == 'tarefa_editada'


# teste de autorização e segurança
def test_autorizacao(client):
    # tentando acessar uma rota sem estar logado
    response = client.post('/usuarios_bp/tarefas', follow_redirects=False)

    # respostas esperadas
    assert response.status_code == 302
    assert '/usuarios_bp/login' in response.headers['location']


# teste de bloqueio
def test_bloqueio(client):
    # Criar um usuário válido
    user = User(nome_usuario='user_bloqueio', senha='senha_correta', email='bloqueio@email.com')
    db.session.add(user)
    db.session.commit()

    # Simular 5 tentativas inválidas de login
    for _ in range(5):
        response = client.post('/usuarios_bp/autenticar', data={
            'usuario': 'user_bloqueio',
            'senha': 'senha_errada'
        }, follow_redirects=True)

    # Recarregar o usuário do banco para pegar o status atualizado
    user = User.query.filter_by(nome_usuario='user_bloqueio').first()

    # Verificar se o usuário foi bloqueado
    assert user.is_locked is True or user.tentativas >= 5

    # Tentar logar novamente com a senha correta (esperado: bloqueado)
    response = client.post('/usuarios_bp/autenticar', data={
        'usuario': 'user_bloqueio',
        'senha': 'senha_correta'
    }, follow_redirects=True)

    assert b'conta foi bloqueada' in response.data or b'bloqueado' in response.data


def test_usuario_inexistente(client):
    # Criar um usuário válido
    user = User(nome_usuario='user_bloqueio', senha='senha_correta', email='bloqueio@email.com')
    db.session.add(user)
    db.session.commit()

    response = client.post('/usuarios_bp/autenticar', data={'usuario': 'inexistente', 'senha': '123456'},
                           follow_redirects=True)

    assert response.status_code == 200
    assert b'Usuario nao encontrado' in response.data


def test_acesso_admin(client):
    # Criando admin
    user = User(nome_usuario='user_admin', senha='senha', email='admin2@email.com', is_admin=True)
    db.session.add(user)
    db.session.commit()

    # Simula login
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)

    # Testando acesso do administrador
    response = client.get('/admin_bp/usuarios', follow_redirects=False)

    # Verificar se a resposta do administrador é bem-sucedida (status 200)
    assert response.status_code == 200
    assert b'usuarios' in response.data


def test_de_acesso_usuario_comum(client):
    user = User(nome_usuario='user_name', senha='senha456', email='user2@email.com', is_admin=False)
    db.session.add(user)
    db.session.commit()

    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)

    response = client.get('/admin_bp/usuarios', follow_redirects=True)

    # A resposta final deve ser 200 (porque seguiu o redirecionamento),
    # mas deve conter a mensagem de acesso negado
    assert response.status_code == 200
    assert b'Acesso negado' in response.data
    assert b'perfil' in response.data
#recuperaçao de senha com token
def test_recuperacao_de_senha_com_token(client):
    #criando usuario para a recuperação de senha
    user = User(nome_usuario='user_recuperacao', senha='senha456', email='testderecuperacao@email.com', is_admin=False)
    db.session.add(user)
    db.session.commit()
    #criando o response com o email que sera cobrado e pegando o post
    response = client.post('/usuarios_bp/recuperar_senha', data={'email':'testderecuperacao@email.com'}, follow_redirects=True)
    usuario = User.query.filter_by(email='testderecuperacao@email.com').first()
    assert usuario is not None
    assert response.status_code == 200
    assert b'email de recuperacao enviado com sucesso' in response.data

def test_reset_de_senha(client):
    # Criando o usuário
    user = User(nome_usuario='user_reset', senha='senha123', email='testreset@email.com', is_admin=False)
    db.session.add(user)
    db.session.commit()

    # Gerando o token para esse usuário
    s = get_serializer()
    token = s.dumps(user.id)

    # Simulando a requisição para o reset de senha com o token
    nova_senha = 'novaSenha456'
    response = client.post(f'/usuarios_bp/resetar_senha/{token}', data={'senha': nova_senha}, follow_redirects=True)

    # Verificando se a senha foi alterada
    usuario = db.session.get(User, user.id)
    assert usuario.verify_password(nova_senha)  # Verificando se a senha foi atualizada corretamente

    # Verificando a resposta
    assert response.status_code == 200
    assert b'senha redefinida com sucesso , faca login ' in response.data

#teste para upload de imagem
def test_upload_imagem_profile(client):
    # Cria o usuário no banco
    user = User(nome_usuario="user_img",senha='123', email="img@test.com")
    db.session.add(user)
    db.session.commit()

    # Simula o login na sessão
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)

    # Dados do formulário (incluindo imagem falsa)
    data = {
        'nome': 'Nick Teste',
        'conteudo': 'Bio de teste',
        'foto': (io.BytesIO(b'imagem fake'), 'foto.jpg')
    }

    # Envia o POST com multipart para simular upload
    response = client.post(
        '/usuarios_bp/profile',
        data=data,
        content_type='multipart/form-data',
        follow_redirects=True
    )

    # Verifica se o perfil foi criado corretamente
    perfil = Profile.query.filter_by(user_id=user.id).first()
    assert response.status_code == 200
    assert perfil is not None
    assert perfil.nome == 'Nick Teste'
    assert perfil.bio == 'Bio de teste'
    assert perfil.foto and 'img/foto.jpg' in perfil.foto