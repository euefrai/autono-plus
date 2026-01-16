from flask import Blueprint, render_template, session, redirect, url_for
from db import get_db

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    # Proteção de rota
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db()
    cur = conn.cursor()

    try:
        # 1. Total de serviços (Geral)
        cur.execute("""
            SELECT SUM(valor) FROM servicos 
            WHERE user_id = %s
        """, (session["user_id"],))
        res_total = cur.fetchone()[0]
        total = float(res_total) if res_total else 0.0

        # 2. Total Pendente
        cur.execute("""
            SELECT SUM(valor) FROM servicos 
            WHERE user_id = %s AND status = 'pendente'
        """, (session["user_id"],))
        res_pendente = cur.fetchone()[0]
        pendente = float(res_pendente) if res_pendente else 0.0

    except Exception as e:
        print(f"Erro no dashboard: {e}")
        total = 0.0
        pendente = 0.0
    finally:
        cur.close()
        conn.close()

    return render_template(
        "dashboard.html",
        nome=session.get("user_nome", "Usuário"),
        total=total,
        pendente=pendente
    )