def is_premium(user):
    """Verifica se o usuário existe e se tem plano premium"""
    if not user:
        return False
    return user.get("plan") == "premium"


def can_create_client(user, total_clients):
    """Verifica se o usuário pode criar um novo cliente baseado no plano"""
    if is_premium(user):
        return True

    from utils.plan_limits import FREE_LIMITS
    # Se total_clients for 3 e o limite for 3, retorna False (bloqueia)
    return total_clients < FREE_LIMITS.get("clients", 3)


def can_create_plano(user, total_planos):
    """Verifica se o usuário pode criar novos planos de serviço"""
    if is_premium(user):
        return True

    from utils.plan_limits import FREE_LIMITS
    return total_planos < FREE_LIMITS.get("planos", 5)


def require_premium(user):
    """Apenas um apelido para is_premium, útil para legibilidade em certas rotas"""
    return is_premium(user)
