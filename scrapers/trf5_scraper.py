import os
import re
import time

import requests

from bs4 import BeautifulSoup
from dotenv import load_dotenv

from scrapers.processo_scraper import ProcessoScraper


# ============================================================
# CONFIGURAÇÃO DO AMBIENTE
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

load_dotenv(
    os.path.join(
        BASE_DIR,
        ".env"
    )
)


# ============================================================
# SCRAPER TRF5
# ============================================================

class TRF5Scraper:

    def __init__(
        self,
        max_threads=10
    ):

        self.base_url = (
            "https://cp.trf5.jus.br"
        )

        self._tempo_inicio = None

        # ----------------------------------------------------
        # CNPJ PROTEGIDO
        # ----------------------------------------------------

        self.cnpj = os.getenv(
            "TRF5_CNPJ"
        )

        if not self.cnpj:

            raise RuntimeError(
                "TRF5_CNPJ não foi configurado. "
                "Crie um arquivo .env na raiz do projeto "
                "contendo TRF5_CNPJ=SEU_CNPJ."
            )

        # Remove caracteres que eventualmente
        # sejam colocados no .env
        self.cnpj = re.sub(
            r"\D",
            "",
            self.cnpj
        )

        if len(self.cnpj) != 14:

            raise RuntimeError(
                "O TRF5_CNPJ configurado no .env "
                "não possui 14 dígitos."
            )

        # ----------------------------------------------------
        # SESSÃO HTTP
        # ----------------------------------------------------

        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36"
            )
        })

        # ----------------------------------------------------
        # SCRAPER DE PROCESSOS
        # ----------------------------------------------------

        self.processo_scraper = ProcessoScraper(
            session=self.session,
            max_threads=max_threads
        )

    # ========================================================
    # BUSCAR PÁGINA
    # ========================================================

    def buscar_pagina(
        self,
        pagina
    ):

        """
        Busca uma página da listagem do TRF5
        e coleta os detalhes dos processos.
        """

        # ----------------------------------------------------
        # CRONÔMETRO
        # ----------------------------------------------------

        if (
            pagina == 1
            or self._tempo_inicio is None
        ):

            self._tempo_inicio = (
                time.perf_counter()
            )

            print(
                "\n" + "=" * 45
            )

            print(
                "⏱️ CRONÔMETRO DE COLETA INICIADO"
            )

            print(
                "=" * 45
            )

        # ----------------------------------------------------
        # URL
        # ----------------------------------------------------

        url = (
            "https://cp.trf5.jus.br/processo/rpvprec/"
            "filtroRPVPrec/cpfcnpj/porData/"
            "tiporpv/ativos/vinculados/"
            f"{self.cnpj}//"
            f"{pagina}"
        )

        # IMPORTANTE:
        # Não imprimimos o CNPJ no terminal.
        print(
            "=============================="
        )

        print(
            f"ACESSANDO PÁGINA {pagina}"
        )

        print(
            "=============================="
        )

        # ----------------------------------------------------
        # REQUISIÇÃO
        # ----------------------------------------------------

        try:

            resposta = self.session.get(
                url,
                timeout=15
            )

            print(
                "STATUS:",
                resposta.status_code
            )

            if resposta.status_code != 200:

                return []

            # ------------------------------------------------
            # HTML
            # ------------------------------------------------

            soup = BeautifulSoup(
                resposta.text,
                "html.parser"
            )

            processos_basicos = (
                self.extrair_processos(
                    soup
                )
            )

            print(
                f"Encontrados "
                f"{len(processos_basicos)} "
                f"processos na página "
                f"{pagina}. "
                f"Coletando detalhes..."
            )

            # ------------------------------------------------
            # DETALHES
            # ------------------------------------------------

            processos_completos = (
                self.processo_scraper
                .extrair_detalhes_em_lote(
                    processos_basicos
                )
            )

            # ------------------------------------------------
            # TEMPO
            # ------------------------------------------------

            tempo_parcial = (
                time.perf_counter()
                - self._tempo_inicio
            )

            print(
                f"⏱️ Tempo acumulado até "
                f"a página {pagina}: "
                f"{tempo_parcial:.2f} segundos\n"
            )

            return processos_completos

        except Exception as e:

            print(
                f"❌ Erro ao buscar página "
                f"{pagina}: {e}"
            )

            return []

    # ========================================================
    # EXTRAIR PROCESSOS
    # ========================================================

    def extrair_processos(
        self,
        soup
    ):

        """
        Varre as tabelas da listagem do TRF5
        e extrai processos, RPVs e links.
        """

        processos = []

        encontrados = set()

        tabelas = soup.find_all(
            "table"
        )

        for tabela in tabelas:

            linhas = tabela.find_all(
                "tr"
            )

            for linha in linhas:

                colunas = linha.find_all(
                    "td"
                )

                if len(colunas) < 3:

                    continue

                texto = " ".join(
                    coluna.get_text(
                        " ",
                        strip=True
                    )
                    for coluna in colunas
                )

                # ------------------------------------------------
                # PROCESSO
                # ------------------------------------------------

                processo = re.search(
                    r"\d{7}-\d{2}\.\d{4}\.4\.05\.\d{4}",
                    texto
                )

                if not processo:

                    continue

                numero = processo.group()

                if numero in encontrados:

                    continue

                encontrados.add(
                    numero
                )

                # ------------------------------------------------
                # RPV
                # ------------------------------------------------

                rpv = re.search(
                    r"RPV\d+-[A-Z]{2}",
                    texto
                )

                numero_rpv = (
                    rpv.group()
                    if rpv
                    else ""
                )

                # ------------------------------------------------
                # LINK
                # ------------------------------------------------

                link = (
                    f"{self.base_url}"
                    f"/processo/{numero}"
                )

                processos.append({
                    "numero": numero,
                    "rpv": numero_rpv,
                    "link": link
                })

        return processos

    # ========================================================
    # COMPATIBILIDADE
    # ========================================================

    def extrair_detalhes_processo(
        self,
        url_ou_processo
    ):

        """
        Método de compatibilidade com
        chamadas antigas.
        """

        if isinstance(
            url_ou_processo,
            dict
        ):

            url = (
                url_ou_processo
                .get(
                    "link",
                    ""
                )
            )

        else:

            url = str(
                url_ou_processo
            )

        return (
            self.processo_scraper
            .extrair_detalhes_processo(
                url
            )
        )