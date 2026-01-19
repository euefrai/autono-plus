from flask import Blueprint, session, redirect, url_for
from db import get_db

billing = Blueprint("billing", __name__)

@billing.route("/upgrade")
def upgrade():
    return render_template("upgrade.html")


@billing.route("/upgrade/success")
def upgrade_success():
    user = session.get("user")
    if not user:
        return redirect(url_for("auth.login"))

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute(
            "UPDATE users SET plan = %s WHERE id = %s",
            ("premium", user["id"])
        )
        conn.commit()

        # 🔥 ATUALIZA A SESSÃO
        user["plan"] = "premium"
        session["user"] = user

    finally:
        cur.close()
        conn.close()

    return redirect(url_for("dashboard.dashboard"))
    
@billing.route("/precos")
def precos():
    user = session.get("user")

    return render_template("precos.html", user=user)

