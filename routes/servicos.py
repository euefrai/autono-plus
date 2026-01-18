from flask import Blueprint, render_template, request, redirect, session, url_for, flash
import urllib.parse
from db import get_db
from utils.plan_limits import FREE_LIMITS

servicos_bp = Blueprint("servicos", __name__)

@servicos_bp.route("/servicos", methods=["GET", "POST"])
def servicos():
    if "user_id" not in session:
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    # CADASTRAR SERVIÇO
    if request.method == "POST":
        # Verificação de Limites do Plano
        cur.execute("SELECT count(*) FROM servicos WHERE user_id = %s", (session["user_id"],))
        total_servicos = cur.fetchone()[0]
        
        # Pega o plano da sessão (certifique-se de salvar no login)
        user_plan = session.get("plan", "free")

        if user_plan == "free" and total_servicos >= FREE_LIMITS.get("services", 10):
            flash("🔒 Limite do plano Free atingido. Faça upgrade.", "warning")
            return redirect(url_for("billing.upgrade"))

        cliente_id = request.form["cliente_id"]
        descricao = request.form["descricao"]
        valor = request.form["valor"]
        data = request.form["data"]
        status = "pendente"

        cur.execute("""
            INSERT INTO servicos (user_id, cliente_id, descricao, valor, data, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (session["user_id"], cliente_id, descricao, valor, data, status))
        conn.commit()

    # LISTAR SERVIÇOS
    cur.execute("""
        SELECT s.id, s.descricao, s.valor, s.data, s.status, c.nome AS cliente_nome, c.telefone
        FROM servicos s
        JOIN clientes c ON c.id = s.cliente_id
        WHERE s.user_id = %s
        ORDER BY s.data DESC
    """, (session["user_id"],))
    servicos_lista = cur.fetchall()

    # BUSCAR CLIENTES PARA O SELECT DO FORMULÁRIO
    cur.execute("SELECT id, nome FROM clientes WHERE user_id = %s", (session["user_id"],))
    clientes_lista = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("servicos.html", servicos=servicos_lista, clientes=clientes_lista)

@servicos_bp.route("/servicos/pagar/<int:id>")
def pagar_servico(id):
    if "user_id" not in session:
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE servicos SET status = 'pago' WHERE id = %s AND user_id = %s",
        (id, session["user_id"])
    )
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("servicos.servicos"))

@servicos_bp.route("/servicos/cobrar/<int:id>")
def cobrar_servico(id):
    if "user_id" not in session:
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.valor, s.descricao, c.nome, c.telefone
        FROM servicos s
        JOIN clientes c ON c.id = s.cliente_id
        WHERE s.id = %s AND s.user_id = %s
    """, (id, session["user_id"]))
    servico = cur.fetchone()
    cur.close()
    conn.close()

    if servico:
        telefone_limpo = "".join(filter(str.isdigit, servico[3]))
        if not telefone_limpo.startswith("55"):
            telefone_limpo = "55" + telefone_limpo
        
        valor_formatado = f"{float(servico[0]):.2f}"
        mensagem = (
            f"Olá {servico[2]} 😊\n"
            f"Serviço: {servico[1]}\n"
            f"Valor: R$ {valor_formatado}\n"
            "Qualquer dúvida fico à disposição!"
        )
        msg_encoded = urllib.parse.quote(mensagem)
        link = f"https://wa.me/{telefone_limpo}?text={msg_encoded}"
        return redirect(link)
    
    return redirect(url_for("servicos.servicos"))

@servicos_bp.route("/servicos/excluir/<int:id>")
def excluir_servico(id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM servicos WHERE id = %s AND user_id = %s",
        (id, session["user_id"])
    )
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("servicos.servicos"))

@servicos_bp.route("/servicos/editar/<int:id>", methods=["GET", "POST"])
def editar_servico(id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        cliente_id = request.form["cliente_id"]
        descricao = request.form["descricao"]
        valor = request.form["valor"]
        data = request.form["data"]
        status = request.form["status"]

        cur.execute("""
            UPDATE servicos
            SET cliente_id = %s, descricao = %s, valor = %s, data = %s, status = %s
            WHERE id = %s AND user_id = %s
        """, (cliente_id, descricao, valor, data, status, id, session["user_id"]))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("servicos.servicos"))

    cur.execute("SELECT * FROM servicos WHERE id = %s AND user_id = %s", (id, session["user_id"]))
    servico = cur.fetchone()

    cur.execute("SELECT id, nome FROM clientes WHERE user_id = %s", (session["user_id"],))
    clientes = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("editar_servico.html", servico=servico, clientes=clientes)