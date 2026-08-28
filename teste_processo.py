from scrapers.processo_scraper import ProcessoScraper


URL = "https://cp.trf5.jus.br/processo/0495051-83.2026.4.05.0000"


scraper = ProcessoScraper()

dados = scraper.extrair_detalhes_processo(URL)

print("\n==========================================")
print("RESULTADO")
print("==========================================")

for chave, valor in dados.items():
    print(f"{chave}: {valor}")