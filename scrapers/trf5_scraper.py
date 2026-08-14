import os
import re
import sys
import time

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from scrapers.processo_scraper import ProcessoScraper


# ============================================================
# CONFIGURAÇÃO DO .ENV
# ============================================================

def obter_caminho_env():

    """
    Localiza o arquivo .env.

    Desenvolvimento:
        __AutoJuris_IA__\.env

    Executável:
        pasta onde o AutoJurisIA.exe está instalado\.env
    """

    if getattr(sys, "frozen", False):

        # Quando estiver rodando como EXE
        pasta_base = os.path.dirname(
            sys.executable
        )

    else:

        # Quando estiver rodando:
        # py main.py
        #
        # Este arquivo está em:
        # scrapers/trf5_scraper.py
        #
        # O .env está em:
        # __AutoJuris_IA__/.env

        pasta_scrapers = os.path.dirname(
            os.path.abspath(__file__)
        )

        pasta_base = os.path.dirname(
            pasta_scrapers
        )

    return os.path.join(
        pasta_base,
        ".env"
    )


# ============================================================
# CARREGAR .ENV
# ============================================================

CAMINHO_ENV = obter_caminho_env()

print(
    "=========================================="
)

print(
    "CARREGANDO CONFIGURAÇÕES DO TRF5"
)

print(
    f"Arquivo .env:"
)

print(
    CAMINHO_ENV
)

print(
    "=========================================="
)


if not os.path.exists(CAMINHO_ENV):

    raise RuntimeError(
        "Arquivo .env não encontrado.\n\n"
        f"Caminho procurado:\n{CAMINHO_ENV}"
    )


load_dotenv(
    CAMINHO_ENV
)


# ============================================================
# CNPJ
# ============================================================

TRF5_CNPJ = os.getenv(
    "TRF5_CNPJ"
)


if not TRF5_CNPJ:

    raise RuntimeError(
        "TRF5_CNPJ não encontrado no arquivo .env.\n\n"
        f"Caminho procurado:\n{CAMINHO_ENV}"
    )


# Remove caracteres que eventualmente tenham sido colocados
# no CNPJ, como pontos, barras e hífen.
TRF5_CNPJ = re.sub(
    r"\D",
    "",
    TRF5_CNPJ
)


if not TRF5_CNPJ:

    raise RuntimeError(
        "O TRF5_CNPJ encontrado no .env está vazio ou inválido."
    )


print(
    "TRF5_CNPJ carregado com sucesso."
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
        # CNPJ
        # ----------------------------------------------------

        self.cnpj = TRF5_CNPJ

        # ----------------------------------------------------
        # CONEXÃO HTTP
        # ----------------------------------------------------

        self.session = requests.Session()

        self.session.headers.update({

            "User-Agent":
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/151.0 Safari/537.36"

        })

        # ----------------------------------------------------
        # PROCESSO SCRAPER
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

        print(
            "=============================="
        )

        print(
            f"ACESSANDO PÁGINA {pagina}:"
        )

        print(
            url
        )

        print(
            "=============================="
        )

        # ----------------------------------------------------
        # REQUEST
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

                print(
                    f"❌ Página {pagina} retornou "
                    f"status {resposta.status_code}"
                )

                return []

            # ------------------------------------------------
            # HTML
            # ------------------------------------------------

            soup = BeautifulSoup(
                resposta.text,
                "html.parser"
            )

            # ------------------------------------------------
            # PROCESSOS BÁSICOS
            # ------------------------------------------------

            processos_basicos = (
                self.extrair_processos(
                    soup
                )
            )

            print(
                f"Encontrados "
                f"{len(processos_basicos)} "
                f"processos na página {pagina}."
            )

            # ------------------------------------------------
            # DETALHES
            # ------------------------------------------------

            if not processos_basicos:

                tempo_parcial = (
                    time.perf_counter()
                    - self._tempo_inicio
                )

                print(
                    f"⏱️ Tempo acumulado: "
                    f"{tempo_parcial:.2f} segundos"
                )

                return []

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

        except requests.RequestException as e:

            print(
                f"❌ Erro HTTP ao buscar "
                f"página {pagina}: {e}"
            )

            return []

        except Exception as e:

            print(
                f"❌ Erro ao buscar "
                f"página {pagina}: {e}"
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
        Varre as tabelas da listagem e extrai:

        - número do processo
        - RPV
        - link
        """

        processos = []

        encontrados = set()

        tabelas = soup.find_all(
            "table"
        )

        # ----------------------------------------------------
        # TABELAS
        # ----------------------------------------------------

        for tabela in tabelas:

            linhas = tabela.find_all(
                "tr"
            )

            # ------------------------------------------------
            # LINHAS
            # ------------------------------------------------

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
                # NÚMERO PROCESSO
                # ------------------------------------------------

                processo = re.search(
                    r"\d{7}-\d{2}\.\d{4}\.4\.05\.\d{4}",
                    texto
                )

                if not processo:
                    continue

                numero = processo.group()

                # ------------------------------------------------
                # DUPLICADOS
                # ------------------------------------------------

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
    # DETALHES DO PROCESSO
    # ========================================================

    def extrair_detalhes_processo(
        self,
        url_ou_processo
    ):

        """
        Método de compatibilidade
        com chamadas antigas.
        """

        if isinstance(
            url_ou_processo,
            dict
        ):

            url = (
                url_ou_processo.get(
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