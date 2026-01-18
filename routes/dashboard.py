from flask import Blueprint, render_template, session, redirect, url_for
from db import get_db

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    # 🔐 Proteção de rota
    user = session.get("user")
    if not user:
        return redirect(url_for("auth.login"))

    db = get_db()

    try:
        # 1️⃣ Total geral (soma de todos os serviços)
        total_res = (
            db.table("servicos")
            .select("valor")
            .eq("user_id", user["id"])
            .execute()
        )

        total = sum(
            float(item["valor"]) for item in (total_res.data or [])
            if item.get("valor") is not None
        )

        # 2️⃣ Total pendente
        pendente_res = (
            db.table("servicos")
            .select("valor")
            .eq("user_id", user["id"])
            .eq("status", "pendente")
            .execute()
        )

        pendente = sum(
            float(item["valor"]) for item in (pendente_res.data or [])
            if item.get("valor") is not None
        )

    except Exception as e:
        print(f"Erro no dashboard: {e}")
        total = 0.0
        pendente = 0.0

    # ✅ PASSANDO user PARA O TEMPLATE (corrige o erro do Jinja)
    return render_template(
        "dashboard.html",
        user=user,
        nome=user.get("nome", "Usuário"),
        total=total,
        pendente=pendente
    )
