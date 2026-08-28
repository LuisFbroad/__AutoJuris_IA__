from scrapers.processo_scraper import ProcessoScraper


# ============================================================
# CONFIGURAÇÃO
# ============================================================

URL_PROCESSO = (
    "https://cp.trf5.jus.br/processo/"
    "0494405-73.2026.4.05.0000"
)


# ============================================================
# TESTE
# ============================================================

print("=" * 70)
print("       TESTE DE DETALHES DO PROCESSO TRF5")
print("=" * 70)

print(f"URL:")
print(URL_PROCESSO)

print("\n" + "=" * 70)
print("CRIANDO PROCESSO SCRAPER")
print("=" * 70)

scraper = ProcessoScraper(
    max_threads=5
)

print("[OK] ProcessoScraper criado.")


# ============================================================
# BUSCAR DETALHES
# ============================================================

print("\n" + "=" * 70)
print("BUSCANDO DETALHES")
print("=" * 70)

dados = scraper.extrair_detalhes_processo(
    URL_PROCESSO
)


# ============================================================
# RESULTADO
# ============================================================

print("\n" + "=" * 70)
print("RESULTADO")
print("=" * 70)

print(f"Tipo do retorno: {type(dados)}")

if isinstance(dados, dict):

    print("\nDados encontrados:")

    for chave, valor in dados.items():
        print(f"{chave:25}: {valor}")

else:

    print("\n[ERRO] O retorno não é um dicionário.")
    print(dados)


print("\n" + "=" * 70)
print("TESTE FINALIZADO")
print("=" * 70)