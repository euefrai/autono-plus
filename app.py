from flask import Flask
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.clientes import clientes_bp
from routes.servicos import servicos_bp
from routes.landing import landing_bp
from config import SECRET_KEY



app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.register_blueprint(clientes_bp)
app.register_blueprint(servicos_bp)
app.register_blueprint(landing_bp)

# Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)

if __name__ == "__main__":
    app.run(debug=True)
