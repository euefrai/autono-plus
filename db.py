import os
import psycopg2

def get_db():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("A variável DATABASE_URL não foi configurada no Render!")
    
    # Adicionando sslmode para garantir a conexão segura com o Supabase
    if "sslmode" not in url:
        url += "?sslmode=require"
        
    return psycopg2.connect(url)
