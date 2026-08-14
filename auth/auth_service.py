import hashlib
import secrets


# ============================================================
# USUÁRIO DO SISTEMA
# ============================================================

USUARIO = "admin"

SENHA_HASH = (
    "f66673975ecb718f0d4f0916aa6c0eb6ee69e8120bc88bd8bd53f6375aec4c55"
)

SALT = (
    "AutoJurisIA_SALT_2026"
)

# ============================================================
# CONFIGURAÇÃO
# ============================================================

ITERACOES = 200_000


# ============================================================
# GERAR HASH
# ============================================================

def gerar_hash_senha(
    senha: str,
    salt: str
):

    return hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt.encode("utf-8"),
        ITERACOES
    ).hex()


# ============================================================
# AUTENTICAR
# ============================================================

def autenticar(
    usuario: str,
    senha: str
):

    usuario = usuario.strip()

    # --------------------------------------------------------
    # VERIFICA USUÁRIO
    # --------------------------------------------------------

    if usuario != USUARIO:

        return False

    # --------------------------------------------------------
    # GERA HASH DA SENHA DIGITADA
    # --------------------------------------------------------

    hash_digitado = gerar_hash_senha(
        senha,
        SALT
    )

    # --------------------------------------------------------
    # COMPARA HASHES
    # --------------------------------------------------------

    return secrets.compare_digest(
        hash_digitado,
        SENHA_HASH
    )