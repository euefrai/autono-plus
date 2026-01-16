from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from utils.db import get_db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        db = get_db()
        # Buscamos o usuário pelo email
        user = db.execute(
            "SELECT * FROM usuarios WHERE email = ?", (email,)
        ).fetchone()
        db.close()

        # Verificamos se o usuário existe e se a senha bate
        if user and check_password_hash(user["senha"], senha):
            session["user_id"] = user["id"]
            session["user_nome"] = user["nome"]
            # Adicionei a role (cargo) que estava sobrando no seu código anterior
            session["role"] = user["role"] if "role" in user.keys() else "user"
            
            return redirect("/dashboard")
        
        else:
            flash("Email ou senha inválidos")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = generate_password_hash(request.form["senha"])

        db = get_db()
        try:
            db.execute(
                "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
                (nome, email, senha)
            )
            db.commit()
            flash("Cadastro realizado com sucesso!")
            return redirect(url_for("auth.login"))
        except:
            flash("Email já cadastrado")
        finally:
            db.close()

    return render_template("auth/register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")