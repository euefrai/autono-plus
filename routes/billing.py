from flask import Blueprint, render_template, session, redirect, url_for, flash
from db import get_db

billing_bp = Blueprint("billing", __name__) # Use o nome que registrou no app.py

@billing_bp.route("/upgrade")
def upgrade():
    return render_template("upgrade.html")

@billing_bp.route("/upgrade/success")
def upgrade_success():
    user = session.get("user")
    if not user:
        return redirect(url_for("auth.login"))

    conn = get_db()
    cur = conn.cursor()

    try:
        # Atualiza no banco de dados Supabase/Postgres
        cur.execute(
            "UPDATE usuarios SET plan = %s WHERE id = %s",
            ("premium", user["id"])
        )
        conn.commit()

        # 🔥 ATUALIZA A SESSÃO
        # Criamos uma cópia para garantir que o Flask detecte a mudança
        updated_user = dict(user)
        updated_user["plan"] = "premium"
        session["user"] = updated_user
        session["plan"] = "premium" # Atualiza a chave solta também
        
        session.modified = True # Força o Flask a salvar a sessão
        flash("Parabéns! Agora você é Premium! ✨", "success")

    except Exception as e:
        print(f"Erro no upgrade: {e}")
        flash("Erro ao processar upgrade.", "danger")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("dashboard.dashboard"))

@billing_bp.route("/precos")
def precos():
    user = session.get("user")
    return render_template("precos.html", user=user)
