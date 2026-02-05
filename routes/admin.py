from flask import Blueprint, render_template, session, redirect, url_for, abort
from db import get_db
import psycopg2.extras


admin_bp = Blueprint("admin", __name__)

# =========================================
# FUNÇÃO AUXILIAR
# =========================================
def verificar_admin():
    """Verifica se o usuário está logado e se possui cargo de admin"""
    user = session.get("user")

    if not user:
        return redirect(url_for("auth.login"))

    if user.get("role") != "admin":
        abort(403)

    return None


# =========================================
# ROTAS DO PAINEL ADMIN
# =========================================

@admin_bp.route("/admin")
def admin_dashboard():
    erro = verificar_admin()
    if erro: return erro
    return render_template("admin/dashboard.html")

@admin_bp.route("/admin/usuarios")
def admin_usuarios():
    erro = verificar_admin()
    if erro: return erro

    conn = get_db()
    cur = conn.cursor()
    
    # Busca a lista de usuários para exibir na tabela do admin
    cur.execute("SELECT id, nome, email, role FROM usuarios ORDER BY id DESC")
    usuarios = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template("admin/usuarios.html", usuarios=usuarios)

@admin_bp.route("/admin/usuarios/excluir/<int:id>")
def excluir_usuario(id):
    erro = verificar_admin()
    if erro: return erro

    conn = get_db()
    cur = conn.cursor()

    try:
        # No PostgreSQL/Supabase usamos %s
        cur.execute("DELETE FROM servicos WHERE user_id = %s", (id,))
        cur.execute("DELETE FROM clientes WHERE user_id = %s", (id,))
        cur.execute("DELETE FROM usuarios WHERE id = %s", (id,))

        # Registro de log
        cur.execute(
            "INSERT INTO logs (acao, usuario_id, data) VALUES (%s, %s, NOW())",
            ("Usuário excluído", id)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Erro ao excluir: {e}")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("admin.admin_usuarios"))

@admin_bp.route("/admin/logs")
def admin_logs():
    erro = verificar_admin()
    if erro:
        return erro

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("""
        SELECT 
            l.id,
            l.acao,
            l.data,
            u.email
        FROM logs l
        LEFT JOIN usuarios u ON u.id = l.usuario_id
        ORDER BY l.id DESC
    """)

    logs = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("admin/logs.html", logs=logs)
