from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db 
import psycopg2.extras

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        conn = get_db()
        # Usamos o RealDictCursor para poder acessar os dados como user['nome'] em vez de user[1]
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            cur.execute("SELECT id, nome, senha, role, plan FROM usuarios WHERE email = %s", (email,))
            user = cur.fetchone()
        finally:
            cur.close()
            conn.close()

        # Agora 'user' é um dicionário. Verificamos a senha:
        if user and check_password_hash(user['senha'], senha):
            # Salvamos os dados na sessão de forma organizada
            session["user_id"] = user['id']
            session["plan"] = user.get('plan', 'free')
            session["nome"] = user['nome']
            
            # Dicionário completo para facilitar no dashboard
            session["user"] = {
                "id": user['id'],
                "nome": user['nome'],
                "email": email,
                "plan": user.get('plan', 'free')
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
            # Garante que o usuário novo sempre comece como 'user' e plano 'free'
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
