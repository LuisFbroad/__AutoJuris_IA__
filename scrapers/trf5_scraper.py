import re
import time
import requests
from bs4 import BeautifulSoup
from scrapers.processo_scraper import ProcessoScraper


class TRF5Scraper:

    def __init__(self, max_threads=10):
        self.base_url = "https://cp.trf5.jus.br"
        self._tempo_inicio = None
        
        # Conexão HTTP Persistente (Keep-Alive)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

        # Instancia o scraper individual reutilizando a mesma sessão
        self.processo_scraper = ProcessoScraper(session=self.session, max_threads=max_threads)

    def buscar_pagina(self, pagina):
        """Busca uma página da listagem do TRF5 e enriquece os dados dos processos em lote."""
        
        # Marca o tempo inicial na primeira página da busca
        if pagina == 1 or self._tempo_inicio is None:
            self._tempo_inicio = time.perf_counter()
            print("\n" + "=" * 45)
            print("⏱️ CRONÔMETRO DE COLETA INICIADO")
            print("=" * 45)

        url = (
            "https://cp.trf5.jus.br/processo/rpvprec/"
            "filtroRPVPrec/cpfcnpj/porData/"
            "tiporpv/ativos/vinculados/"
            "17391998000103//"
            f"{pagina}"
        )

        print(f"==============================\nACESSANDO PÁGINA {pagina}: {url}\n==============================")

        try:
            resposta = self.session.get(url, timeout=15)
            print("STATUS:", resposta.status_code)
            if resposta.status_code != 200:
                return []

            soup = BeautifulSoup(resposta.text, "html.parser")
            processos_basicos = self.extrair_processos(soup)

            print(f"Encontrados {len(processos_basicos)} processos na página {pagina}. Coletando detalhes...")

            # Executa a busca paralela dos detalhes para todos os processos encontrados
            processos_completos = self.processo_scraper.extrair_detalhes_em_lote(processos_basicos)
            
            # Imprime o tempo decorrido atualizado no terminal
            tempo_parcial = time.perf_counter() - self._tempo_inicio
            print(f"⏱️ Tempo acumulado até a página {pagina}: {tempo_parcial:.2f} segundos\n")

            return processos_completos

        except Exception as e:
            print(f"❌ Erro ao buscar página {pagina}: {e}")
            return []

    def extrair_processos(self, soup):
        """Varre a tabela da listagem e extrai os números, RPVs e links básicos."""
        processos = []
        encontrados = set()

        tabelas = soup.find_all("table")

        for tabela in tabelas:
            linhas = tabela.find_all("tr")

            for linha in linhas:
                colunas = linha.find_all("td")
                if len(colunas) < 3:
                    continue

                texto = " ".join(coluna.get_text(" ", strip=True) for coluna in colunas)

                processo = re.search(r"\d{7}-\d{2}\.\d{4}\.4\.05\.\d{4}", texto)
                if not processo:
                    continue

                numero = processo.group()
                if numero in encontrados:
                    continue

                encontrados.add(numero)

                rpv = re.search(r"RPV\d+-[A-Z]{2}", texto)
                numero_rpv = rpv.group() if rpv else ""

                link = f"{self.base_url}/processo/{numero}"

                processos.append({
                    "numero": numero,
                    "rpv": numero_rpv,
                    "link": link
                })

        return processos

    def extrair_detalhes_processo(self, url_ou_processo):
        """Método de compatibilidade com chamadas antigas."""
        if isinstance(url_ou_processo, dict):
            url = url_ou_processo.get("link", "")
        else:
            url = str(url_ou_processo)

        return self.processo_scraper.extrair_detalhes_processo(url)