from flask import redirect, url_for, flash, session
from models.planos import count_planos_by_user
from utils.permissions import can_create_plano

@planos_bp.route("/planos/create", methods=["POST"])
def create_plano():
    user = session.get("user")

    total_planos = count_planos_by_user(user["id"])

    if not can_create_plano(user, total_planos):
        flash("🔒 O plano Free permite apenas 1 plano ativo.", "warning")
        return redirect(url_for("billing.upgrade"))

    # continua criação normal
