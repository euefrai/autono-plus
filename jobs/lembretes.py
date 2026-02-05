from db import get_db
from utils.whatsapp import enviar_whatsapp
from datetime import date

def enviar_lembretes():
    hoje = date.today()

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT s.id, c.telefone, s.descricao
        FROM servicos s
        JOIN clientes c ON c.id = s.cliente_id
        WHERE s.data = %s
        AND s.status = 'pendente'
        AND s.lembrete_enviado = false
    """, (hoje,))

    servicos = cur.fetchall()

    for s_id, telefone, descricao in servicos:
        msg = f"Olá! 👋 Lembrete do serviço: {descricao}. Qualquer dúvida, estamos à disposição 😊"
        
        if enviar_whatsapp(telefone, msg):
            cur.execute(
                "UPDATE servicos SET lembrete_enviado = true WHERE id = %s",
                (s_id,)
            )

    conn.commit()
    cur.close()
    conn.close()
