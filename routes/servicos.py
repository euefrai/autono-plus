from flask import Blueprint, render_template, request, redirect, session
from utils.db import get_db

servicos_bp = Blueprint("servicos", __name__)

@servicos_bp.route("/servicos", methods=["GET", "POST"])
def servicos():
    if "user_id" not in session:
        return redirect("/")

    db = get_db()

    # CADASTRAR SERVIÇO
    if request.method == "POST":
        cliente_id = request.form["cliente_id"]
        descricao = request.form["descricao"]
        valor = request.form["valor"]
        data = request.form["data"]
        status = "pendente"

        db.execute("""
            INSERT INTO servicos (user_id, cliente_id, descricao, valor, data, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session["user_id"], cliente_id, descricao, valor, data, status))
        db.commit()

    # LISTAR SERVIÇOS
    servicos = db.execute("""
        SELECT s.*, c.nome AS cliente_nome
        FROM servicos s
        JOIN clientes c ON c.id = s.cliente_id
        WHERE s.user_id = ?
        ORDER BY s.data DESC
    """, (session["user_id"],)).fetchall()

    clientes = db.execute(
        "SELECT id, nome FROM clientes WHERE user_id = ?",
        (session["user_id"],)
    ).fetchall()

    db.close()
    return render_template("servicos.html", servicos=servicos, clientes=clientes)


@servicos_bp.route("/servicos/pagar/<int:id>")
def pagar_servico(id):
    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    db.execute(
        "UPDATE servicos SET status = 'pago' WHERE id = ? AND user_id = ?",
        (id, session["user_id"])
    )
    db.commit()
    db.close()

    return redirect("/servicos")


from utils.whatsapp import gerar_link_whatsapp

@servicos_bp.route("/servicos/cobrar/<int:id>")
def cobrar_servico(id):
    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    servico = db.execute("""
        SELECT s.valor, s.descricao, c.nome, c.telefone
        FROM servicos s
        JOIN clientes c ON c.id = s.cliente_id
        WHERE s.id = ? AND s.user_id = ?
    """, (id, session["user_id"])).fetchone()
    db.close()

    mensagem = (
        f"Olá {servico['nome']} 😊\n"
        f"Serviço: {servico['descricao']}\n"
        f"Valor: R$ {servico['valor']:.2f}\n"
        "Qualquer dúvida fico à disposição!"
    )

    link = gerar_link_whatsapp(servico["telefone"], mensagem)
    return redirect(link)


@servicos_bp.route("/servicos/excluir/<int:id>")
def excluir_servico(id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    db.execute(
        "DELETE FROM servicos WHERE id = ? AND user_id = ?",
        (id, session["user_id"])
    )
    db.commit()
    db.close()

    return redirect("/servicos")


@servicos_bp.route("/servicos/editar/<int:id>", methods=["GET", "POST"])
def editar_servico(id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()

    if request.method == "POST":
        cliente_id = request.form["cliente_id"]
        descricao = request.form["descricao"]
        valor = request.form["valor"]
        data = request.form["data"]
        status = request.form["status"]

        db.execute("""
            UPDATE servicos
            SET cliente_id = ?, descricao = ?, valor = ?, data = ?, status = ?
            WHERE id = ? AND user_id = ?
        """, (cliente_id, descricao, valor, data, status, id, session["user_id"]))
        db.commit()
        db.close()
        return redirect("/servicos")

    servico = db.execute("""
        SELECT * FROM servicos
        WHERE id = ? AND user_id = ?
    """, (id, session["user_id"])).fetchone()

    clientes = db.execute(
        "SELECT id, nome FROM clientes WHERE user_id = ?",
        (session["user_id"],)
    ).fetchall()

    db.close()
    return render_template(
        "editar_servico.html",
        servico=servico,
        clientes=clientes
    )
