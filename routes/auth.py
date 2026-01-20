from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db 
import psycopg2.extras
from utils.logger import registrar_log

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        conn = get_db()
        # Usamos RealDictCursor para poder acessar user['email'] em vez de user[0]
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            cur.execute(
                "SELECT id, nome, email, plan, role, senha FROM usuarios WHERE email = %s",
                (email,)
            )
            user = cur.fetchone()

            if not user or not check_password_hash(user["senha"], senha):
                flash("Login inválido. Verifique seu e-mail e senha.", "danger")
                return render_template("auth/login.html")

            # 1. Registra o log ANTES de redirecionar
            registrar_log("Login realizado", user["id"])

            # 2. Salva o dicionário completo para o context_processor do app.py
            session["user"] = {
                "id": user["id"],
                "nome": user["nome"],
                "email": user["email"],
                "plan": user["plan"],
                "role": user["role"]
            }

            # Mantemos as chaves soltas por compatibilidade com suas rotas antigas
            session["user_id"] = user["id"]
            session["plan"] = user["plan"]
            session["nome"] = user["nome"]

            return redirect(url_for("dashboard.dashboard"))

        except Exception as e:
            print(f"Erro no login: {e}")
            flash("Ocorreu um erro interno. Tente novamente.", "danger")
        finally:
            cur.close()
            conn.close()

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
            cur.execute(
                "INSERT INTO usuarios (nome, email, senha, role, plan) VALUES (%s, %s, %s, %s, %s)",
                (nome, email, senha_hash, "user", "free")
            )
            conn.commit()
            flash("Cadastro realizado com sucesso! Faça seu login.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            conn.rollback()
            print(f"Erro no registro: {e}")
            flash("Este e-mail já está cadastrado ou ocorreu um erro.", "danger")
        finally:
            cur.close()
            conn.close()

    return render_template("auth/register.html")

@auth_bp.route("/logout")
def logout():
    # Pegamos o ID antes de limpar a sessão
    user_id = session.get("user", {}).get("id") or session.get("user_id")
    if user_id:
        registrar_log("Logout", user_id)
        
    session.clear()
    return redirect(url_for("auth.login"))