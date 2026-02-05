import os
from flask import Blueprint, render_template, session, redirect, url_for, flash
from db import get_db
import stripe

billing_bp = Blueprint("billing", __name__)

# O ideal é colocar 'STRIPE_SECRET_KEY' nas variáveis de ambiente do Render
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY") or "pk_test_51SrIyBAFW4QJRJWyQzDHnu5blXRp719ktGP4TJulimvImSh4WbeM5ZkU3uN0RvLLDP8KyJAjo6BuyxMnoNMCWnko00AlVNzw5i"

@billing_bp.route("/precos")
def precos():
    user = session.get("user")
    return render_template("precos.html", user=user)

@billing_bp.route("/pagar/premium")
def pagar_premium():
    user = session.get("user")
    if not user:
        flash("Por favor, faça login para continuar.", "warning")
        return redirect(url_for("auth.login"))

    try:
        # Criando a sessão de checkout única
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "brl",
                    "product_data": {
                        "name": "Plano Premium - Autono Plus",
                        "description": "Acesso ilimitado e cobrança via WhatsApp",
                    },
                    "unit_amount": 999,  # R$ 1,89
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=url_for("billing.upgrade_success", _external=True),
            cancel_url=url_for("billing.precos", _external=True),
            customer_email=user.get("email")
        )
        # O code=303 é recomendado para redirecionamentos após POST/ações de pagamento
        return redirect(checkout_session.url, code=303)
    
    except Exception as e:
        print(f"Erro no Stripe: {e}")
        flash("Erro ao iniciar pagamento. Tente novamente.", "danger")
        return redirect(url_for("billing.precos"))

@billing_bp.route("/upgrade/success")
def upgrade_success():
    user = session.get("user")
    if not user:
        return redirect(url_for("auth.login"))

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute(
            "UPDATE usuarios SET plan = %s WHERE id = %s",
            ("premium", user["id"])
        )
        conn.commit()

        # Atualiza o objeto na sessão
        user["plan"] = "premium"
        session["user"] = user
        session["plan"] = "premium"
        session.modified = True
        
        flash("Parabéns! Seu plano foi atualizado para Premium! ✨", "success")
    except Exception as e:
        print(f"Erro ao atualizar banco: {e}")
        flash("Erro ao ativar plano. Contate o suporte.", "danger")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("dashboard.dashboard"))


@billing_bp.route("/stripe/sucesso")
def stripe_sucesso():
    return redirect(url_for("billing.upgrade_success"))
