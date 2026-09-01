import os
import traceback
from dotenv import load_dotenv

from scrapers.trf5_scraper import TRF5Scraper


# ============================================================
# CONFIGURAÇÃO
# ============================================================

load_dotenv()

DOCUMENTO = "89957709291"
TIPO_DOCUMENTO = "CPF"
PAGINA = 1
MAX_THREADS = 5


# ============================================================
# CABEÇALHO
# ============================================================

print("=" * 70)
print("       TESTE DIRETO DO TRF5")
print("=" * 70)

print(f"Documento: {DOCUMENTO}")
print(f"Tipo: {TIPO_DOCUMENTO}")
print(f"Página testada: {PAGINA}")

print("=" * 70)


# ============================================================
# CRIAR SCRAPER
# ============================================================

print()
print("[1/3] Criando TRF5Scraper...")

try:

    scraper = TRF5Scraper(
        documento=DOCUMENTO,
        tipo_documento=TIPO_DOCUMENTO,
        max_threads=MAX_THREADS
    )

    print("[OK] TRF5Scraper criado.")

except Exception as e:

    print()
    print("=" * 70)
    print("ERRO AO CRIAR TRF5Scraper")
    print("=" * 70)

    print(e)
    traceback.print_exc()

    raise SystemExit(1)


# ============================================================
# CONFIGURAÇÕES
# ============================================================

print()
print("=" * 70)
print("[2/3] CONFIGURAÇÕES")
print("=" * 70)

print(
    f"Documento utilizado: "
    f"{getattr(scraper, 'documento', DOCUMENTO)}"
)

print(
    f"Tipo de documento: "
    f"{getattr(scraper, 'tipo_documento', TIPO_DOCUMENTO)}"
)

print(
    f"Threads: "
    f"{getattr(scraper, 'max_threads', MAX_THREADS)}"
)

print(
    f"Página: {PAGINA}"
)

print(
    f"Base URL: "
    f"{getattr(scraper, 'base_url', os.getenv('TRF5_BASE_URL'))}"
)


# ============================================================
# BUSCAR PÁGINA
# ============================================================

print()
print("[3/3] Buscando processos...")
print()

try:

    # IMPORTANTE:
    # buscar_pagina() atualmente recebe somente a página.
    resultado = scraper.buscar_pagina(PAGINA)

except Exception as e:

    print()
    print("=" * 70)
    print("ERRO AO BUSCAR PÁGINA")
    print("=" * 70)

    print(e)
    traceback.print_exc()

    raise SystemExit(1)


# ============================================================
# ANALISAR RETORNO
# ============================================================

print()
print("=" * 70)
print("              RESULTADO")
print("=" * 70)

print()

print("Tipo do retorno:")
print(type(resultado))

print()


# ============================================================
# CASO O SCRAPER RETORNE DICIONÁRIO
# ============================================================

if isinstance(resultado, dict):

    print("Chaves encontradas:")

    for chave in resultado.keys():
        print(f" - {chave}")

    print()

    processos = resultado.get("processos", [])

    total = resultado.get(
        "total",
        len(processos)
    )

    print(f"Total informado pelo TRF5: {total}")
    print(f"Processos retornados: {len(processos)}")


# ============================================================
# CASO O SCRAPER RETORNE LISTA
# ============================================================

elif isinstance(resultado, list):

    processos = resultado

    print(
        f"Processos retornados: "
        f"{len(processos)}"
    )


# ============================================================
# OUTRO TIPO
# ============================================================

else:

    print(
        "O scraper retornou um tipo inesperado."
    )

    print()
    print("Conteúdo retornado:")
    print(resultado)

    raise SystemExit(1)


# ============================================================
# EXIBIR PROCESSOS
# ============================================================

print()
print("-" * 70)

if not processos:

    print("NENHUM PROCESSO ENCONTRADO.")

else:

    for indice, processo in enumerate(
        processos,
        start=1
    ):

        print()
        print(f"PROCESSO {indice}")
        print("-" * 40)

        # ----------------------------------------------------
        # PROCESSO COMO DICIONÁRIO
        # ----------------------------------------------------

        if isinstance(processo, dict):

            print(
                "Processo:",
                processo.get("processo", "")
            )

            print(
                "Processo originário:",
                processo.get(
                    "processo_originario",
                    ""
                )
            )

            print(
                "RPV:",
                processo.get("rpv", "")
            )

            print(
                "Nome:",
                processo.get("nome", "")
            )

            print(
                "Vara:",
                processo.get("vara", "")
            )

            print(
                "Banco:",
                processo.get("banco", "")
            )

            print(
                "Data decisão:",
                processo.get(
                    "data_decisao",
                    ""
                )
            )

            print(
                "Data movimento:",
                processo.get(
                    "data_movimento",
                    ""
                )
            )

            print(
                "Hora movimento:",
                processo.get(
                    "hora_movimento",
                    ""
                )
            )

            print(
                "Situação:",
                processo.get(
                    "situacao",
                    ""
                )
            )

            print(
                "Link:",
                processo.get(
                    "link",
                    ""
                )
            )

        # ----------------------------------------------------
        # PROCESSO COMO STRING
        # ----------------------------------------------------

        else:

            print(
                "Valor:",
                processo
            )


# ============================================================
# RESUMO
# ============================================================

print()
print("=" * 70)
print("                    RESUMO")
print("=" * 70)

print()

print(
    f"Documento : {DOCUMENTO}"
)

print(
    f"Tipo      : {TIPO_DOCUMENTO}"
)

print(
    f"Página    : {PAGINA}"
)

print(
    f"Processos : {len(processos)}"
)

print()

print("=" * 70)
print("              TESTE FINALIZADO")
print("=" * 70)
print()