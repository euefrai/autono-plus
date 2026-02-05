from db import get_db

def count_planos_by_user(user_id):
    db = get_db()

    response = (
        db.table("planos")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .execute()
    )

    return response.count or 0