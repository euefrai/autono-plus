from flask import Blueprint, render_template, request, redirect, session, url_for, flash
import urllib.parse
from db import get_db
from utils.plan_limits import FREE_LIMITS
from utils.permissions import require_premium 
from datetime import date

servicos_bp = Blueprint("servicos", __name__)

@servicos_bp.route("/servicos", methods=["GET", "POST"])
def servicos():
    if "user_id" not in session:
        return redirect("/")

    user_id = session.get("user_id")
    conn = get_db()
    cur = conn.cursor()

    # --- 1. CADASTRAR SERVIÇO (POST) ---
    if request.method == "POST":
        user_plan = session.get("plan", "free")
        
        # Verificação de Limite de Plano
        cur.execute("SELECT count(*) FROM servicos WHERE user_id = %s", (user_id,))
        total_atual = cur.fetchone()[0]
        
        if user_plan == "free" and total_atual >= FREE_LIMITS.get("services", 10):
            flash("🔒 Limite de serviços do plano Free atingido.", "warning")
            cur.close()
            conn.close()
            return redirect(url_for("billing.upgrade"))

        # Coleta de dados do formulário
        cliente_id = request.form.get("cliente_id")
        descricao = request.form.get("descricao")
        valor = request.form.get("valor")
        data_servico = request.form.get("data_servico")
        data_vencimento = request.form.get("data_vencimento")

        try:
            # UNIFICADO: Apenas um INSERT com todos os campos novos
            cur.execute("""
                INSERT INTO servicos (
                    user_id, cliente_id, descricao, valor, status, data_servico, data_vencimento
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_id, cliente_id, descricao, valor, "pendente", data_servico, data_vencimento))
            
            conn.commit()
            flash("Serviço cadastrado com sucesso!", "success")
        except Exception as e:
            conn.rollback()
            print(f"Erro ao inserir serviço: {e}")
            flash("Erro ao salvar serviço no banco de dados.", "danger")

    # --- 2. PREPARAÇÃO DE DADOS PARA O HTML (GET) ---
    # Filtros da listagem
    status_filtro = request.args.get("status") or None
    busca = request.args.get("q") or None

    # Listagem de serviços com filtros opcionais
    query = """
        SELECT s.id,
               s.descricao,
               s.valor,
               s.data_servico,
               s.status,
               c.nome AS cliente_nome,
               c.telefone,
               s.data_vencimento
        FROM servicos s
        JOIN clientes c ON c.id = s.cliente_id
        WHERE s.user_id = %s
    """
    params = [user_id]

    if status_filtro in ("pendente", "pago"):
        query += " AND s.status = %s"
        params.append(status_filtro)

    if busca:
        query += " AND (c.nome ILIKE %s OR s.descricao ILIKE %s)"
        like = f"%{busca}%"
        params.extend([like, like])

    query += " ORDER BY s.data_servico DESC"

    cur.execute(query, tuple(params))
    servicos_lista = cur.fetchall()

    # Lista de clientes para o formulário
    cur.execute("SELECT id, nome FROM clientes WHERE user_id = %s ORDER BY nome", (user_id,))
    clientes_lista = cur.fetchall()

    # Contador para o template (evita o erro 'Undefined')
    cur.execute("SELECT count(*) FROM servicos WHERE user_id = %s", (user_id,))
    total_para_template = cur.fetchone()[0]

    cur.close()
    conn.close()

    return render_template(
        "servicos.html", 
        servicos=servicos_lista, 
        clientes=clientes_lista, 
        total_servicos=total_para_template,
        hoje=date.today()
    )

# --- OUTRAS ROTAS (COBRAR, PAGAR, EXCLUIR, EDITAR) ---

@servicos_bp.route("/servicos/cobrar/<int:id>")
def cobrar_servico(id):
    if "user_id" not in session: return redirect("/")

    user = {"plan": session.get("plan", "free")}
    if not require_premium(user):
        flash("⭐ A cobrança via WhatsApp é exclusiva para usuários Premium!", "info")
        return redirect(url_for("billing.upgrade"))

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
        telefone_limpo = "".join(filter(str.isdigit, str(servico[3])))
        if not telefone_limpo.startswith("55"): telefone_limpo = "55" + telefone_limpo
        
        msg = f"Olá {servico[2]} 😊\nServiço: {servico[1]}\nValor: R$ {float(servico[0]):.2f}"
        return redirect(f"https://wa.me/{telefone_limpo}?text={urllib.parse.quote(msg)}")
    
    return redirect(url_for("servicos.servicos"))

@servicos_bp.route("/servicos/pagar/<int:id>")
def pagar_servico(id):
    if "user_id" not in session: return redirect("/")
    conn = get_db(); cur = conn.cursor()
    cur.execute("UPDATE servicos SET status = 'pago' WHERE id = %s AND user_id = %s", (id, session["user_id"]))
    conn.commit(); cur.close(); conn.close()
    return redirect(url_for("servicos.servicos"))

@servicos_bp.route("/servicos/excluir/<int:id>")
def excluir_servico(id):
    if "user_id" not in session: return redirect("/login")
    conn = get_db(); cur = conn.cursor()
    cur.execute("DELETE FROM servicos WHERE id = %s AND user_id = %s", (id, session["user_id"]))
    conn.commit(); cur.close(); conn.close()
    return redirect(url_for("servicos.servicos"))

@servicos_bp.route("/servicos/editar/<int:id>", methods=["GET", "POST"])
def editar_servico(id):
    if "user_id" not in session: return redirect("/login")
    conn = get_db(); cur = conn.cursor()

    if request.method == "POST":
        cur.execute("""
            UPDATE servicos
            SET cliente_id = %s, descricao = %s, valor = %s, data_servico = %s, data_vencimento = %s, status = %s
            WHERE id = %s AND user_id = %s
        """, (request.form["cliente_id"], request.form["descricao"], request.form["valor"], 
              request.form["data_servico"], request.form["data_vencimento"], request.form["status"], id, session["user_id"]))
        conn.commit(); cur.close(); conn.close()
        return redirect(url_for("servicos.servicos"))

    cur.execute("SELECT * FROM servicos WHERE id = %s AND user_id = %s", (id, session["user_id"]))
    servico = cur.fetchone()
    cur.execute("SELECT id, nome FROM clientes WHERE user_id = %s", (session["user_id"],))
    clientes = cur.fetchall()
    cur.close(); conn.close()
    return render_template("editar_servico.html", servico=servico, clientes=clientes)