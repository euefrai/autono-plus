from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db  # kkkkk to trocando os bancos direto kakakskska

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        conn = get_db()
        cur = conn.cursor()
        
        # Selecionamos os campos necessários
        cur.execute("SELECT id, nome, senha, role, plan FROM usuarios WHERE email = %s", (email,))
        user = cur.fetchone()
        
        cur.close()
        conn.close()

        # Verificamos se o usuário existe e a senha bate
        if user and check_password_hash(user[2], senha):
            # Salva os dados na sessão acessando pelos índices da tupla
            # user[0]=id, user[1]=nome, user[2]=senha, user[3]=role, user[4]=plan
            session["user_id"] = user[0]
            session["nome"] = user[1]
            session["role"] = user[3]
            session["plan"] = user[4] if len(user) > 4 else "free"
            
            # Também salvamos o dicionário 'user' se você usar assim em outras partes
            session["user"] = {
                "id": user[0],
                "nome": user[1],
                "email": email,
                "plan": user[4] if len(user) > 4 else "free"
            }

            return redirect(url_for("dashboard.dashboard"))
        
        else:
            flash("Email ou senha inválidos", "danger")

    return render_template("auth/login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha_hash = generate_password_hash(request.form.get("senha"))

        conn = get_db()
        cur = conn.cursor()
        try:
            # Inserindo com os campos padrão
            cur.execute(
                "INSERT INTO usuarios (nome, email, senha, role, plan) VALUES (%s, %s, %s, %s, %s)",
                (nome, email, senha_hash, "user", "free")
            )
            conn.commit()
            flash("Cadastro realizado com sucesso!", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            conn.rollback()
            print(f"Erro no registro: {e}")
            flash("Erro ao cadastrar: Email já existe ou problema no servidor.", "danger")
        finally:
            cur.close()
            conn.close()

    return render_template("auth/register.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))