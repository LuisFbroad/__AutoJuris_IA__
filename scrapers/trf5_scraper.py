import os
import re
import time
import requests

from bs4 import BeautifulSoup
from dotenv import load_dotenv

from scrapers.processo_scraper import ProcessoScraper


# ============================================================
# CONFIGURAÇÃO
# ============================================================

load_dotenv()

TRF5_BASE_URL = os.getenv(
    "TRF5_BASE_URL",
    "https://cp.trf5.jus.br"
).rstrip("/")


# ============================================================
# SCRAPER TRF5
# ============================================================

class TRF5Scraper:

    def __init__(
        self,
        documento,
        tipo_documento="CPF",
        max_threads=5
    ):
        if not documento:
            raise ValueError(
                "Documento não informado ou inválido."
            )

        self.documento = re.sub(
            r"\D",
            "",
            str(documento)
        )

        if not self.documento:
            raise ValueError(
                "Documento não informado ou inválido."
            )

        self.tipo_documento = (
            tipo_documento or "CPF"
        ).upper()

        self.max_threads = max_threads

        self.base_url = TRF5_BASE_URL

        # ========================================================
        # SESSÃO HTTP
        # ========================================================

        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/151.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,image/avif,"
                "image/webp,*/*;q=0.8"
            ),
            "Accept-Language": "pt-BR,pt;q=0.9",
        })

    # ============================================================
    # MONTAR URL DA CONSULTA
    # ============================================================

    def montar_url(self, pagina=1):

        # O TRF5 usa índice de página começando em 0.
        pagina_indice = max(
            int(pagina) - 1,
            0
        )

        url = (
            f"{self.base_url}/processo/rpvprec/"
            f"filtroRPVPrec/cpfcnpj/porData/"
            f"tiporpv/ativos/vinculados/"
            f"{self.documento}//{pagina_indice}"
        )

        return url

    # ============================================================
    # EXTRAIR TOTAL
    # ============================================================

    def extrair_total(self, soup):

        texto = soup.get_text(
            " ",
            strip=True
        )

        # Exemplo:
        #
        # CPF/CNPJ: 89957709291
        # ...
        # Total: 385
        #

        match = re.search(
            r"\bTotal\s*:\s*(\d+)",
            texto,
            re.IGNORECASE
        )

        if match:
            return int(
                match.group(1)
            )

        return 0

    # ============================================================
    # EXTRAIR PROCESSOS DA PÁGINA
    # ============================================================

    def extrair_processos(self, soup):

        processos = []

        # ========================================================
        # PROCURA TODOS OS LINKS DE PROCESSO
        # ========================================================

        links = soup.find_all("a")

        padrao_processo = re.compile(
            r"\b\d{7}-\d{2}\.\d{4}\.4\.05\.\d{4}\b"
        )

        padrao_rpv = re.compile(
            r"\bRPV\s*\d+\s*-\s*[A-Z]{2}\b",
            re.IGNORECASE
        )

        vistos = set()

        for link in links:

            href = link.get(
                "href",
                ""
            ).strip()

            texto_link = link.get_text(
                " ",
                strip=True
            )

            # ====================================================
            # VERIFICA SE É UM LINK DE PROCESSO
            # ====================================================

            match_processo = padrao_processo.search(
                texto_link
            )

            if not match_processo:
                continue

            processo = match_processo.group(0)

            # ====================================================
            # EVITA DUPLICADOS
            # ====================================================

            if processo in vistos:
                continue

            vistos.add(processo)

            # ====================================================
            # URL ABSOLUTA
            # ====================================================

            if href.startswith("http://") or href.startswith(
                "https://"
            ):
                url_processo = href
            else:
                url_processo = (
                    self.base_url
                    + "/"
                    + href.lstrip("/")
                )

            # ====================================================
            # PROCURA RPV
            # ====================================================

            rpv = ""

            # Normalmente o RPV está na mesma linha/tabela.
            elemento_pai = link

            for _ in range(5):

                if not elemento_pai:
                    break

                texto_pai = elemento_pai.get_text(
                    " ",
                    strip=True
                )

                match_rpv = padrao_rpv.search(
                    texto_pai
                )

                if match_rpv:
                    rpv = (
                        match_rpv.group(0)
                        .replace(" ", "")
                        .upper()
                    )
                    break

                elemento_pai = elemento_pai.parent

            # ====================================================
            # DATA E HORA DO MOVIMENTO
            # ====================================================

            data_movimento = ""
            hora_movimento = ""

            # A informação fica na mesma linha da tabela.
            linha = link.find_parent("tr")

            if linha:

                texto_linha = linha.get_text(
                    " ",
                    strip=True
                )

                # Data
                match_data = re.search(
                    r"\b\d{2}/\d{2}/\d{4}\b",
                    texto_linha
                )

                if match_data:
                    data_movimento = (
                        match_data.group(0)
                    )

                # Hora
                match_hora = re.search(
                    r"\b\d{2}:\d{2}\b",
                    texto_linha
                )

                if match_hora:
                    hora_movimento = (
                        match_hora.group(0)
                    )

            # ====================================================
            # SITUAÇÃO
            # ====================================================

            situacao = ""

            if linha:

                texto_linha = linha.get_text(
                    " ",
                    strip=True
                )

                if re.search(
                    r"Processo\s+Arquivado",
                    texto_linha,
                    re.IGNORECASE
                ):
                    situacao = "Processo Arquivado"

                elif re.search(
                    r"Processo\s+Ativo",
                    texto_linha,
                    re.IGNORECASE
                ):
                    situacao = "Processo Ativo"

            # ====================================================
            # ADICIONA PROCESSO
            # ====================================================

            processos.append({
                "link": url_processo,
                "processo": processo,
                "processo_originario": "",
                "rpv": rpv,
                "nome": "",
                "vara": "",
                "banco": "",
                "data_decisao": "",
                "data_movimento": data_movimento,
                "hora_movimento": hora_movimento,
                "situacao": situacao,
            })

        return processos

    # ============================================================
    # BUSCAR UMA PÁGINA
    # ============================================================

    def buscar_pagina(
        self,
        pagina=1
    ):

        print()
        print("=" * 60)
        print(
            f"ACESSANDO PÁGINA {pagina}"
        )
        print("=" * 60)

        url = self.montar_url(
            pagina
        )

        print(url)
        print()

        inicio = time.time()

        try:

            # ====================================================
            # REQUEST
            # ====================================================

            print(
                "[TRF5] Iniciando requisição HTTP..."
            )

            print(
                "[TRF5] Timeout: 30 segundos"
            )

            resposta = self.session.get(
                url,
                timeout=30
            )

            tempo = time.time() - inicio

            print(
                f"[TRF5] Resposta recebida em "
                f"{tempo:.2f} segundos"
            )

            print(
                f"[TRF5] Status HTTP: "
                f"{resposta.status_code}"
            )

            print(
                f"[TRF5] Tamanho: "
                f"{len(resposta.content)} bytes"
            )

            print(
                f"[TRF5] Encoding: "
                f"{resposta.encoding}"
            )

            print(
                f"[TRF5] URL final: "
                f"{resposta.url}"
            )

            if resposta.status_code != 200:

                raise RuntimeError(
                    f"TRF5 retornou HTTP "
                    f"{resposta.status_code}"
                )

            # ====================================================
            # BEAUTIFULSOUP
            # ====================================================

            print(
                "[TRF5] Criando BeautifulSoup..."
            )

            soup = BeautifulSoup(
                resposta.text,
                "html.parser"
            )

            print(
                "[TRF5] BeautifulSoup criado."
            )

            # ====================================================
            # TOTAL
            # ====================================================

            print(
                "[TRF5] Extraindo total..."
            )

            total = self.extrair_total(
                soup
            )

            print(
                f"[TRF5] Total encontrado: "
                f"{total}"
            )

            # ====================================================
            # PROCESSOS
            # ====================================================

            print(
                "[TRF5] Extraindo processos..."
            )

            processos = self.extrair_processos(
                soup
            )

            print(
                f"[TRF5] Processos encontrados: "
                f"{len(processos)}"
            )

            for indice, processo in enumerate(
                processos,
                start=1
            ):

                print(
                    f"  [{indice}] "
                    f"{processo.get('processo', '')} | "
                    f"{processo.get('rpv', '')} | "
                    f"{processo.get('data_movimento', '')} "
                    f"{processo.get('hora_movimento', '')}"
                )

            print()

            print(
                "[TRF5] Página processada com sucesso."
            )

            # ====================================================
            # RETORNO
            # ====================================================

            return {
                "pagina": pagina,
                "total": total,
                "processos": processos
            }

        except Exception as e:

            print()
            print("=" * 60)
            print(
                "[TRF5] ERRO AO PROCESSAR PÁGINA"
            )
            print("=" * 60)
            print(e)

            raise

    # ============================================================
    # BUSCAR PÁGINA + DETALHES
    # ============================================================

    def buscar_pagina_com_detalhes(
        self,
        pagina=1
    ):

        resultado = self.buscar_pagina(
            pagina=pagina
        )

        processos = resultado.get(
            "processos",
            []
        )

        if not processos:

            return resultado

        print()
        print("=" * 60)
        print(
            "EXTRAINDO DETALHES DOS PROCESSOS"
        )
        print("=" * 60)

        print(
            f"Processos para detalhar: "
            f"{len(processos)}"
        )

        # ========================================================
        # PROCESSO SCRAPER
        # ========================================================

        processo_scraper = ProcessoScraper(
            session=self.session,
            max_threads=self.max_threads
        )

        # ========================================================
        # EXTRAÇÃO EM LOTE
        # ========================================================

        processos_completos = (
            processo_scraper.extrair_detalhes_em_lote(
                processos
            )
        )

        # ========================================================
        # GARANTE QUE DADOS DA LISTAGEM
        # NÃO SEJAM PERDIDOS
        # ========================================================

        for original, completo in zip(
            processos,
            processos_completos
        ):

            if not completo.get("processo"):
                completo["processo"] = (
                    original.get("processo", "")
                )

            if not completo.get("rpv"):
                completo["rpv"] = (
                    original.get("rpv", "")
                )

            if not completo.get("data_movimento"):
                completo["data_movimento"] = (
                    original.get(
                        "data_movimento",
                        ""
                    )
                )

            if not completo.get("hora_movimento"):
                completo["hora_movimento"] = (
                    original.get(
                        "hora_movimento",
                        ""
                    )
                )

            if not completo.get("situacao"):
                completo["situacao"] = (
                    original.get(
                        "situacao",
                        ""
                    )
                )

            if not completo.get("link"):
                completo["link"] = (
                    original.get("link", "")
                )

        resultado["processos"] = (
            processos_completos
        )

        print()
        print(
            "[TRF5] Detalhes extraídos."
        )

        return resultado

    # ============================================================
    # BUSCAR VÁRIAS PÁGINAS
    # ============================================================

    def buscar_todas_paginas(
        self,
        max_paginas=None,
        extrair_detalhes=True
    ):

        print()
        print("=" * 60)
        print(
            "INICIANDO COLETA COMPLETA DO TRF5"
        )
        print("=" * 60)

        todos_processos = []

        # ========================================================
        # PRIMEIRA PÁGINA
        # ========================================================

        if extrair_detalhes:

            resultado_primeira = (
                self.buscar_pagina_com_detalhes(
                    pagina=1
                )
            )

        else:

            resultado_primeira = (
                self.buscar_pagina(
                    pagina=1
                )
            )

        total = resultado_primeira.get(
            "total",
            0
        )

        processos_primeira = (
            resultado_primeira.get(
                "processos",
                []
            )
        )

        todos_processos.extend(
            processos_primeira
        )

        # ========================================================
        # CALCULAR NÚMERO DE PÁGINAS
        #
        # O TRF5 mostrou:
        #
        # Total: 385
        # 10 processos por página
        #
        # Portanto:
        #
        # ceil(385 / 10) = 39 páginas
        # ========================================================

        processos_por_pagina = 10

        total_paginas = (
            (total + processos_por_pagina - 1)
            // processos_por_pagina
        )

        if max_paginas is not None:

            total_paginas = min(
                total_paginas,
                max_paginas
            )

        print()
        print(
            f"[TRF5] Total de processos: {total}"
        )

        print(
            f"[TRF5] Total estimado de páginas: "
            f"{total_paginas}"
        )

        # ========================================================
        # DEMAIS PÁGINAS
        # ========================================================

        for pagina in range(
            2,
            total_paginas + 1
        ):

            if extrair_detalhes:

                resultado = (
                    self.buscar_pagina_com_detalhes(
                        pagina=pagina
                    )
                )

            else:

                resultado = (
                    self.buscar_pagina(
                        pagina=pagina
                    )
                )

            processos = resultado.get(
                "processos",
                []
            )

            todos_processos.extend(
                processos
            )

            print()
            print(
                f"[TRF5] Progresso: "
                f"{pagina}/{total_paginas} páginas"
            )

            print(
                f"[TRF5] Processos coletados: "
                f"{len(todos_processos)}"
            )

        # ========================================================
        # RETORNO FINAL
        # ========================================================

        return {
            "total": total,
            "total_paginas": total_paginas,
            "processos": todos_processos
        }

    def comparar_resultados(
    self,
    primeira_busca,
    segunda_busca
    ):

        mapa_1 = {
            processo.get("processo"): processo
            for processo in primeira_busca
            if processo.get("processo")
        }

        mapa_2 = {
            processo.get("processo"): processo
            for processo in segunda_busca
            if processo.get("processo")
        }

        ids_1 = set(mapa_1.keys())
        ids_2 = set(mapa_2.keys())

        adicionados = ids_2 - ids_1
        removidos = ids_1 - ids_2
        mantidos = ids_1 & ids_2

        return {
            "igual": ids_1 == ids_2,
            "adicionados": list(adicionados),
            "removidos": list(removidos),
            "mantidos": list(mantidos),
            "total_primeira": len(ids_1),
            "total_segunda": len(ids_2)
        }

    def comparar_resultados(
        self,
        primeira_busca,
        segunda_busca
    ):

        mapa_1 = {
            processo.get("processo"): processo
            for processo in primeira_busca
            if processo.get("processo")
        }

        mapa_2 = {
            processo.get("processo"): processo
            for processo in segunda_busca
            if processo.get("processo")
        }

        ids_1 = set(mapa_1.keys())
        ids_2 = set(mapa_2.keys())

        adicionados = ids_2 - ids_1
        removidos = ids_1 - ids_2
        mantidos = ids_1 & ids_2

        return {
            "igual": ids_1 == ids_2,
            "adicionados": list(adicionados),
            "removidos": list(removidos),
            "mantidos": list(mantidos),
            "total_primeira": len(ids_1),
            "total_segunda": len(ids_2)
        }