from flask import Blueprint, render_template

billing = Blueprint("billing", __name__)

@billing.route("/upgrade")
def upgrade():
    return render_template("upgrade.html")
