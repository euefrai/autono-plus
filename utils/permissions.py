def is_premium(user):
    return user.get("plan") == "premium"


def can_create_client(user, total_clients):
    if is_premium(user):
        return True

    from utils.plan_limits import FREE_LIMITS
    return total_clients < FREE_LIMITS["clients"]

def can_create_plano(user, total_planos):
    if user.get("plan") == "premium":
        return True

    from utils.plan_limits import FREE_LIMITS
    return total_planos < FREE_LIMITS["planos"]
