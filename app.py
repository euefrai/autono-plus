import os
from flask import Flask
from dotenv import load_dotenv

# 1. Carrega as variáveis de ambiente antes de importar as rotas
load_dotenv()

from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.clientes import clientes_bp
from routes.servicos import servicos_bp
from routes.landing import landing_bp
from routes.admin import admin_bp
from routes.billing import billing_bp

app = Flask(__name__)

# 2. Configuração de segurança
# Prioriza a chave do .env/Render, se não existir, usa a do config.py
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") or "uma_chave_padrao_muito_segura"

# 3. Registro dos Blueprints (Agrupados para melhor leitura)
app.register_blueprint(landing_bp)   # Geralmente a página inicial
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(servicos_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(billing_bp)

if __name__ == "__main__":
    # O debug deve ser True apenas localmente
    app.run(debug=True)
