from scrapers.trf5_scraper import TRF5Scraper
from scrapers.processo_scraper import ProcessoScraper


# ============================================================
# CONFIGURAÇÃO
# ============================================================

DOCUMENTO = "89957709291"
TIPO_DOCUMENTO = "CPF"
PAGINA = 1
MAX_THREADS = 5


# ============================================================
# CABEÇALHO
# ============================================================

print("=" * 70)
print("       TESTE DE INTEGRAÇÃO DOS SCRAPERS TRF5")
print("=" * 70)

print(f"Documento : {DOCUMENTO}")
print(f"Tipo      : {TIPO_DOCUMENTO}")
print(f"Página    : {PAGINA}")
print(f"Threads   : {MAX_THREADS}")


# ============================================================
# 1 - SCRAPER DA LISTAGEM
# ============================================================

print("\n" + "=" * 70)
print("[1/2] BUSCANDO LISTAGEM DO TRF5")
print("=" * 70)

trf5 = TRF5Scraper(
    documento=DOCUMENTO,
    tipo_documento=TIPO_DOCUMENTO,
    max_threads=MAX_THREADS
)

resultado = trf5.buscar_pagina(
    pagina=PAGINA
)


# ============================================================
# VERIFICAR RESULTADO
# ============================================================

if not isinstance(resultado, dict):

    print("\n[ERRO] Retorno inesperado do TRF5:")
    print(resultado)
    raise SystemExit(1)


processos = resultado.get(
    "processos",
    []
)

total = resultado.get(
    "total",
    0
)


print("\n" + "-" * 70)
print(f"Total informado pelo TRF5 : {total}")
print(f"Processos encontrados     : {len(processos)}")
print("-" * 70)


if not processos:

    print("\n[ERRO] Nenhum processo encontrado.")
    raise SystemExit(1)


# ============================================================
# MOSTRAR LISTAGEM
# ============================================================

print("\nPROCESSOS DA LISTAGEM:")

for i, processo in enumerate(processos, start=1):

    print(
        f"[{i:02}] "
        f"{processo.get('processo', '')} | "
        f"{processo.get('rpv', '')} | "
        f"{processo.get('data_movimento', '')}"
    )


# ============================================================
# 2 - SCRAPER DE DETALHES
# ============================================================

print("\n" + "=" * 70)
print("[2/2] EXTRAINDO DETALHES DOS PROCESSOS")
print("=" * 70)

processo_scraper = ProcessoScraper(
    max_threads=MAX_THREADS
)


processos_completos = (
    processo_scraper.extrair_detalhes_em_lote(
        processos
    )
)


# ============================================================
# RESULTADO FINAL
# ============================================================

print("\n" + "=" * 70)
print("              RESULTADO FINAL")
print("=" * 70)

print(
    f"Processos processados: "
    f"{len(processos_completos)}"
)


# ============================================================
# EXIBIR PROCESSOS
# ============================================================

for i, processo in enumerate(
    processos_completos,
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
print("                    RESUMO")
print("=" * 70)

print(f"Documento             : {DOCUMENTO}")
print(f"Tipo                  : {TIPO_DOCUMENTO}")
print(f"Página                : {PAGINA}")
print(f"Total no TRF5         : {total}")
print(f"Processos na página   : {len(processos)}")
print(f"Processos detalhados  : {len(processos_completos)}")

print("\n" + "=" * 70)
print("              TESTE FINALIZADO")
print("=" * 70)