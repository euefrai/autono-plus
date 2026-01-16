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

@clientes_bp.route("/clientes/excluir/<int:id>")
def excluir_cliente(id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()

    # Exclui serviços do cliente primeiro (importante)
    db.execute(
        "DELETE FROM servicos WHERE cliente_id = ? AND user_id = ?",
        (id, session["user_id"])
    )

    # Exclui o cliente
    db.execute(
        "DELETE FROM clientes WHERE id = ? AND user_id = ?",
        (id, session["user_id"])
    )

    db.commit()
    db.close()

    return redirect("/clientes")


@clientes_bp.route("/clientes/editar/<int:id>", methods=["GET", "POST"])
def editar_cliente(id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()

    if request.method == "POST":
        nome = request.form["nome"]
        telefone = request.form["telefone"]
        observacao = request.form["observacao"]

        db.execute("""
            UPDATE clientes
            SET nome = ?, telefone = ?, observacao = ?
            WHERE id = ? AND user_id = ?
        """, (nome, telefone, observacao, id, session["user_id"]))
        db.commit()
        db.close()
        return redirect("/clientes")

    cliente = db.execute("""
        SELECT * FROM clientes
        WHERE id = ? AND user_id = ?
    """, (id, session["user_id"])).fetchone()
    db.close()

    return render_template("editar_cliente.html", cliente=cliente)

