from db import get_db

def count_planos_by_user(user_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM planos WHERE user_id = ?",
        (user_id,)
    )

    total = cursor.fetchone()[0]
    db.close()
    return total
