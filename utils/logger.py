from db import get_db

def registrar_log(acao, usuario_id=None):
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO logs (acao, usuario_id) VALUES (%s, %s)",
            (acao, usuario_id)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Erro ao registrar log:", e)
    finally:
        cur.close()
        conn.close()
