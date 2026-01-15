from flask import Blueprint, render_template, request, redirect, session
from utils.db import get_db

clientes_bp = Blueprint("clientes", __name__)

@clientes_bp.route("/clientes", methods=["GET", "POST"])
def clientes():
    if "user_id" not in session:
        return redirect("/")

    db = get_db()

    # CRIAR CLIENTE
    if request.method == "POST":
        nome = request.form["nome"]
        telefone = request.form["telefone"]
        observacao = request.form["observacao"]

        db.execute(
            "INSERT INTO clientes (user_id, nome, telefone, observacao) VALUES (?, ?, ?, ?)",
            (session["user_id"], nome, telefone, observacao)
        )
        db.commit()

    # LISTAR CLIENTES
    clientes = db.execute(
        "SELECT * FROM clientes WHERE user_id = ?",
        (session["user_id"],)
    ).fetchall()

    db.close()
    return render_template("clientes.html", clientes=clientes)
