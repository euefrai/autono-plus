import urllib.parse
import requests
import os

def gerar_link_whatsapp(telefone, mensagem):
    texto = urllib.parse.quote(mensagem)
    return f"https://wa.me/55{telefone}?text={texto}"


def enviar_whatsapp(numero, mensagem):
    url = f"https://graph.facebook.com/v18.0/{os.getenv('WHATSAPP_PHONE_ID')}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": mensagem}
    }

    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
        "Content-Type": "application/json"
    }

    r = requests.post(url, json=payload, headers=headers)
    return r.status_code == 200

