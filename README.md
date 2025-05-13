# 🎮 Blog Gamer – Projeto Flask

Este é um projeto web desenvolvido com Flask que simula um blog gamer. A aplicação permite que usuários se cadastrem, façam login, editem seu perfil com foto e bio, postem críticas, comentem, e que administradores gerenciem o sistema através de um painel.

---

## 🧩 Funcionalidades

- Cadastro e login de usuários
- Recuperação de senha por e-mail
- Perfil com nome, bio e imagem de perfil
- Criação de críticas/posts com comentários
- Área administrativa com painel para admins
- Sistema de autorização (usuário comum e admin)
- Proteção com Flask-Talisman
- Responsividade com Bootstrap
- Flash messages estilizadas
- Templates com herança base

---

## 🛠️ Tecnologias e ferramentas

- **Python 3**
- **Flask**
- SQLite
- Bootstrap 5
- Flask-Login
- Flask-Mail
- Flask-WTF
- Flask-Migrate
- Flask-Talisman
- Jinja2
- HTML5 + CSS3

---

## 🧑‍💻 Autor

- **João Carlos Lima da Cunha**
- E-mail: [jocajclc@gmail.com](mailto:jocajclc@gmail.com)
- GitHub: [João no GitHub](https://github.com/rhufy)

## 🚀 Como executar localmente

```bash
# Clone o repositório
git clone https://github.com/rhufy/meu-primeiro-projeto-flask.git

# Acesse a pasta do projeto
cd meu-primeiro-projeto-flask

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate     # Linux/macOS
venv\Scripts\activate        # Windows

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
flask run
