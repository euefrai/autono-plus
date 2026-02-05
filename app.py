import os
from flask import Flask, session
from dotenv import load_dotenv

# 1. Carrega as variáveis de ambiente antes de qualquer outra coisa
load_dotenv()

# Importação dos Blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.clientes import clientes_bp
from routes.servicos import servicos_bp
from routes.landing import landing_bp
from routes.admin import admin_bp
from routes.billing import billing_bp

app = Flask(__name__)

# 2. Configuração de segurança
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") or "uma_chave_padrao_muito_segura"

# 3. Registro dos Blueprints
app.register_blueprint(landing_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(servicos_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(billing_bp)

# 4. Injeção Global de Variáveis (Melhorado para evitar erros de None)
@app.context_processor
def inject_user():
    user_data = session.get("user") # Tenta pegar o dicionário completo que salvamos no auth.py
    
    if not user_data:
        # Se não houver sessão, retorna valores vazios para não quebrar o HTML
        user_data = {
            "id": session.get("user_id"),
            "plan": session.get("plan", "free"),
            "nome": session.get("nome")
        }
        
    return {"user": user_data}

if __name__ == "__main__":
    app.run(debug=True)