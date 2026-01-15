from flask import Blueprint, render_template, session, redirect
from utils.db import get_db

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    db = get_db()

    total = db.execute("""
        SELECT SUM(valor) FROM servicos
        WHERE user_id = ?
    """, (session["user_id"],)).fetchone()[0] or 0

    pendente = db.execute("""
        SELECT SUM(valor) FROM servicos
        WHERE user_id = ? AND status = 'pendente'
    """, (session["user_id"],)).fetchone()[0] or 0

    db.close()

    return render_template(
        "dashboard.html",
        nome=session["user_nome"],
        total=total,
        pendente=pendente
    )
