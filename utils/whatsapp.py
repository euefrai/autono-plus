import urllib.parse

def gerar_link_whatsapp(telefone, mensagem):
    texto = urllib.parse.quote(mensagem)
    return f"https://wa.me/55{telefone}?text={texto}"
