from flask import Blueprint, render_template, session, redirect
from db import get_db

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect("/login")
    return render_template("admin/dashboard.html")


@admin_bp.route("/admin/usuarios")
def admin_usuarios():
    if session.get("role") != "admin":
        return redirect("/login")

    db = get_db()
    usuarios = db.execute(
        "SELECT id, nome, email, role FROM usuarios"
    ).fetchall()
    db.close()

    return render_template("admin/usuarios.html", usuarios=usuarios)


@admin_bp.route("/admin/usuarios/excluir/<int:id>")
def excluir_usuario(id):
    if session.get("role") != "admin":
        return redirect("/login")

    db = get_db()

    db.execute("DELETE FROM servicos WHERE user_id = ?", (id,))
    db.execute("DELETE FROM clientes WHERE user_id = ?", (id,))
    db.execute("DELETE FROM usuarios WHERE id = ?", (id,))

    db.execute(
        "INSERT INTO logs (acao, usuario_id, data) VALUES (?, ?, datetime('now'))",
        ("Usuário excluído", id)
    )

    db.commit()
    db.close()

    return redirect("/admin/usuarios")


@admin_bp.route("/admin/logs")
def admin_logs():
    if session.get("role") != "admin":
        return redirect("/login")

    db = get_db()
    logs = db.execute("""
        SELECT l.acao, l.data, u.email
        FROM logs l
        LEFT JOIN usuarios u ON u.id = l.usuario_id
        ORDER BY l.id DESC
    """).fetchall()
    db.close()

    return render_template("admin/logs.html", logs=logs)
