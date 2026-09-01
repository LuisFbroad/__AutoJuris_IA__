from services.trf5_service import TRF5Service


# ============================================================
# CONFIGURAÇÕES
# ============================================================

DOCUMENTO = "89957709291"
TIPO_DOCUMENTO = "CPF"
PAGINA = 1
THREADS = 5


# ============================================================
# CABEÇALHO
# ============================================================

print("=" * 70)
print("       TESTE DO TRF5 SERVICE")
print("=" * 70)

print(
    f"Documento: {DOCUMENTO}"
)


# ============================================================
# CRIAR SERVICE
# ============================================================

print("\nCriando TRF5Service...")

service = TRF5Service(
    max_threads=THREADS
)

print("[OK] Service criado.")


# ============================================================
# COLETA
# ============================================================

print("\nIniciando coleta...")

resultado = service.coletar_processos(
    documento=DOCUMENTO,
    tipo_documento=TIPO_DOCUMENTO,
    limite_paginas=PAGINA,
    extrair_detalhes=True
)


# ============================================================
# RESULTADO
# ============================================================

print("\n" + "=" * 70)
print("RESULTADO")
print("=" * 70)


print(
    f"Total no TRF5: "
    f"{resultado.get('total', 0)}"
)


processos = resultado.get(
    "processos",
    []
)


print(
    f"Processos coletados: "
    f"{len(processos)}"
)


# ============================================================
# PROCESSOS
# ============================================================

for i, processo in enumerate(
    processos,
    start=1
):

    print("\n" + "-" * 70)
    print(f"PROCESSO {i}")
    print("-" * 70)

    print(
        f"Processo              : "
        f"{processo.get('processo', '')}"
    )

    print(
        f"Processo originário   : "
        f"{processo.get('processo_originario', '')}"
    )

    print(
        f"RPV                   : "
        f"{processo.get('rpv', '')}"
    )

    print(
        f"Nome                  : "
        f"{processo.get('nome', '')}"
    )

    print(
        f"Vara                  : "
        f"{processo.get('vara', '')}"
    )

    print(
        f"Banco                 : "
        f"{processo.get('banco', '')}"
    )

    print(
        f"Data decisão          : "
        f"{processo.get('data_decisao', '')}"
    )

    print(
        f"Data movimento        : "
        f"{processo.get('data_movimento', '')}"
    )

    print(
        f"Hora movimento        : "
        f"{processo.get('hora_movimento', '')}"
    )

    print(
        f"Situação              : "
        f"{processo.get('situacao', '')}"
    )

    print(
        f"Link                  : "
        f"{processo.get('link', '')}"
    )


# ============================================================
# RESUMO
# ============================================================

print("\n" + "=" * 70)
print("RESUMO")
print("=" * 70)

print(
    f"Documento             : {DOCUMENTO}"
)

print(
    f"Tipo                  : {TIPO_DOCUMENTO}"
)

print(
    f"Página                : {PAGINA}"
)

print(
    f"Total no TRF5         : "
    f"{resultado.get('total', 0)}"
)

print(
    f"Processos coletados   : "
    f"{len(processos)}"
)

print("=" * 70)
print("TESTE FINALIZADO")
print("=" * 70)