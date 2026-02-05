from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from db import get_db
from utils.permissions import can_create_client, require_premium # Importe as duas
from models.cliente import count_clients_by_user

clientes_bp = Blueprint("clientes", __name__)

@clientes_bp.route("/clientes", methods=["GET", "POST"])
def clientes():
    if "user_id" not in session:
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    # CRIAR CLIENTE
    if request.method == "POST":
        user_id = session.get("user_id")
        user_plan = session.get("plan", "free")
        
        # Simula objeto user para a permissão
        user = {"id": user_id, "plan": user_plan}
        
        # ❌ REMOVI o require_premium daqui, pois o plano Free pode criar até o limite.
        # Se você quer que Clientes seja SÓ para Premium, mantenha o require, 
        # mas se quer permitir o teste (limite de 3), use apenas o can_create_client.

        # Verifica limite do plano antes de inserir
        total_clients = count_clients_by_user(user_id)
        if not can_create_client(user, total_clients):
            flash("🔒 Limite do plano Free atingido. Faça upgrade para continuar.", "warning")
            return redirect(url_for("billing.upgrade"))

        nome = request.form["nome"]
        telefone = request.form["telefone"]
        observacao = request.form["observacao"]

        cur.execute(
            "INSERT INTO clientes (user_id, nome, telefone, observacao) VALUES (%s, %s, %s, %s)",
            (user_id, nome, telefone, observacao)
        )
        conn.commit()

    # LISTAR CLIENTES (com busca opcional)
    busca = request.args.get("q") or None

    if busca:
        cur.execute(
            """
            SELECT id, nome, telefone, observacao
            FROM clientes
            WHERE user_id = %s
              AND (nome ILIKE %s OR telefone ILIKE %s)
            ORDER BY nome
            """,
            (session["user_id"], f"%{busca}%", f"%{busca}%"),
        )
    else:
        cur.execute(
            """
            SELECT id, nome, telefone, observacao
            FROM clientes
            WHERE user_id = %s
            ORDER BY nome
            """,
            (session["user_id"],),
        )
    clientes_lista = cur.fetchall()

    cur.close()
    conn.close()
    
    # IMPORTANTE: Passe o total_clients para o template para o contador funcionar
    total_atual = count_clients_by_user(session.get("user_id"))
    return render_template("clientes.html", clientes=clientes_lista, total_clients=total_atual)

# ... (restante das rotas excluir e editar permanecem iguais)

@clientes_bp.route("/clientes/excluir/<int:id>")
def excluir_cliente(id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    try:
        # Exclui serviços do cliente primeiro (integridade referencial)
        cur.execute(
            "DELETE FROM servicos WHERE cliente_id = %s AND user_id = %s",
            (id, session["user_id"])
        )
        # Exclui o cliente
        cur.execute(
            "DELETE FROM clientes WHERE id = %s AND user_id = %s",
            (id, session["user_id"])
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Erro ao excluir cliente: {e}")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("clientes.clientes"))

@clientes_bp.route("/clientes/editar/<int:id>", methods=["GET", "POST"])
def editar_cliente(id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        nome = request.form["nome"]
        telefone = request.form["telefone"]
        observacao = request.form["observacao"]

        cur.execute("""
            UPDATE clientes
            SET nome = %s, telefone = %s, observacao = %s
            WHERE id = %s AND user_id = %s
        """, (nome, telefone, observacao, id, session["user_id"]))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("clientes.clientes"))

    # Busca dados para o formulário de edição
    cur.execute("""
        SELECT id, nome, telefone, observacao FROM clientes
        WHERE id = %s AND user_id = %s
    """, (id, session["user_id"]))
    cliente = cur.fetchone()
    
    cur.close()
    conn.close()

    return render_template("editar_cliente.html", cliente=cliente)
