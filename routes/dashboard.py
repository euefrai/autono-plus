from flask import Blueprint, render_template, session, redirect, url_for
from db import get_db

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    user = session.get("user")
    if not user:
        return redirect(url_for("auth.login"))

    conn = get_db()
    cur = conn.cursor()

    try:
        # Total geral
        cur.execute("""
            SELECT COALESCE(SUM(valor), 0)
            FROM servicos
            WHERE user_id = %s
        """, (user["id"],))
        total = float(cur.fetchone()[0])

        # Total pendente
        cur.execute("""
            SELECT COALESCE(SUM(valor), 0)
            FROM servicos
            WHERE user_id = %s AND status = 'pendente'
        """, (user["id"],))
        pendente = float(cur.fetchone()[0])

    except Exception as e:
        print("Erro no dashboard:", e)
        total = 0.0
        pendente = 0.0
    finally:
        cur.close()
        conn.close()

    return render_template(
        "dashboard.html",
        user=user,
        nome=user.get("nome", "Usuário"),
        total=total,
        pendente=pendente
    )
