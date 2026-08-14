import os
import sqlite3


# ============================================================
# CAMINHO DO BANCO
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

AUTH_DIR = os.path.join(
    BASE_DIR,
    "auth"
)

DATABASE_PATH = os.path.join(
    AUTH_DIR,
    "users.db"
)


# ============================================================
# CONEXÃO
# ============================================================

def conectar():

    os.makedirs(
        AUTH_DIR,
        exist_ok=True
    )

    conexao = sqlite3.connect(
        DATABASE_PATH
    )

    conexao.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conexao.commit()

    return conexao