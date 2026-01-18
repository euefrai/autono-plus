from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from utils.db import get_db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        conn = get_db()
        cur = conn.cursor() # Necessário para PostgreSQL
        
        # Mudamos de '?' para '%s'
        cur.execute("SELECT id, nome, senha, role FROM usuarios WHERE email = %s", (email,))
        user = cur.fetchone()
        
        cur.close()
        conn.close()

    # Verificamos se o usuário existe (user não é None)
        if user and check_password_hash(user[2], senha): # user[2] é a senha no SELECT acima
            session["user_id"] = user[0]
            session["user_nome"] = user[1]
            session["role"] = user[3] if len(user) > 3 else "user"
            
            return redirect(url_for("dashboard.dashboard")) # Use url_for por segurança
        
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
            # Mudamos de '?' para '%s'
            cur.execute(
                "INSERT INTO usuarios (nome, email, senha, role) VALUES (%s, %s, %s, %s)",
                (nome, email, senha_hash, "user")
            )
            conn.commit()
            flash("Cadastro realizado com sucesso!", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            conn.rollback()
            flash("Erro ao cadastrar: Email já existe ou problema no servidor.", "danger")
        finally:
            cur.close()
            conn.close()

    return render_template("auth/register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
