from flask import Blueprint, session, redirect, url_for
from db import get_db

billing = Blueprint("billing", __name__)

@billing.route("/upgrade")
def upgrade():
    return render_template("upgrade.html")


@billing.route("/upgrade/success")
def upgrade_success():
    user = session.get("user")
    db = get_db()

    # Atualiza plano no Supabase
    db.table("users").update(
        {"plan": "premium"}
    ).eq(
        "id", user["id"]
    ).execute()

    # Atualiza sessão
    user["plan"] = "premium"
    session["user"] = user

    return redirect(url_for("dashboard.index"))