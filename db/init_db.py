import sqlite3
import os

DB_PATH = "db/database.db"

os.makedirs("db", exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# =========================
# USUÁRIOS
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL
)
""")

# =========================
# CLIENTES
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    nome TEXT NOT NULL,
    telefone TEXT,
    observacao TEXT
)
""")

# =========================
# SERVIÇOS
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS servicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    cliente_id INTEGER,
    descricao TEXT,
    valor REAL,
    data TEXT,
    status TEXT
)
""")

conn.commit()
conn.close()

print("✅ Banco de dados criado com sucesso!")
