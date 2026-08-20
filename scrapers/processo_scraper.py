import re
import requests

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed


ESTADOS_BRASIL = {
    "PERNAMBUCO": "PE",
    "RECIFE": "PE",
    "CABO DE SANTO AGOSTINHO": "PE",
    "CABO": "PE",
    "- PE": "PE",
    " PE": "PE",

    "ALAGOAS": "AL",
    "MACEIÓ": "AL",
    "MACEIO": "AL",
    "- AL": "AL",
    " AL": "AL",

    "CEARÁ": "CE",
    "CEARA": "CE",
    "FORTALEZA": "CE",
    "- CE": "CE",
    " CE": "CE",

    "SERGIPE": "SE",
    "ARACAJU": "SE",
    "- SE": "SE",
    " SE": "SE",

    "RIO GRANDE DO NORTE": "RN",
    "NATAL": "RN",
    "- RN": "RN",
    " RN": "RN",

    "PARAÍBA": "PB",
    "PARAIBA": "PB",
    "JOÃO PESSOA": "PB",
    "JOAO PESSOA": "PB",
    "- PB": "PB",
    " PB": "PB"
}


class ProcessoScraper:

    def __init__(self, session=None, max_threads=10):
        # Utiliza a sessão do TRF5Scraper ou cria uma nova
        self.session = session or requests.Session()
        self.max_threads = max_threads

        if "User-Agent" not in self.session.headers:
            self.session.headers.update({
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/151.0.0.0 Safari/537.36"
                )
            })

    def extrair_detalhes_processo(self, url):
        """Extrai os detalhes de um único processo."""

        try:
            resposta = self.session.get(url, timeout=10)

            if resposta.status_code != 200:
                return {
                    "link": url,
                    "processo": "",
                    "rpv": "",
                    "vara": "",
                    "banco": "",
                    "data_decisao": ""
                }

            soup = BeautifulSoup(resposta.text, "html.parser")

            # Texto da página
            texto = soup.get_text("\n", strip=True)

            dados = {
                "link": url,
                "processo": "",
                "rpv": "",
                "vara": "",
                "banco": "",
                "data_decisao": ""
            }

            # ==========================================================
            # PROCESSO
            # ==========================================================

            # Procura especificamente por número no padrão CNJ:
            #
            # 0002886-98.2018.4.03.6182
            #
            # Isso evita pegar o PROC. ORIGINÁRIO.

            processo = re.search(
                r"PROCESSO\s*(?:N[º°]|NÂº|NÃº)?\s*:?\s*"
                r"(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})",
                texto,
                re.IGNORECASE
            )

            if processo:
                dados["processo"] = processo.group(1).strip()

            # ==========================================================
            # RPV
            # ==========================================================

            # Primeiro tenta encontrar o identificador no formato:
            #
            # RPV3916938-SE
            #
            # RPV + números + estado

            rpv_codigo = re.search(
                r"\bRPV\d+[A-Z]{2}\b",
                texto,
                re.IGNORECASE
            )

            if rpv_codigo:
                dados["rpv"] = rpv_codigo.group(0).strip().upper()

            # ==========================================================
            # FALLBACK - NÚMERO DO REQUISITÓRIO
            # ==========================================================

            # Caso a página não tenha "RPV3916938-SE",
            # procura pelo campo NÚMERO DO REQUISITÓRIO.

            if not dados["rpv"]:

                rpv_requisitorio = re.search(
                    r"N[ÚUÃ]MERO\s+DO\s+REQUISIT[ÓOÃ]RIO"
                    r"\s*:?\s*([^\n\r]+)",
                    texto,
                    re.IGNORECASE
                )

                if rpv_requisitorio:
                    dados["rpv"] = (
                        rpv_requisitorio
                        .group(1)
                        .strip()
                    )

            # ==========================================================
            # FALLBACK 2 - REQUISITÓRIO
            # ==========================================================

            if not dados["rpv"]:

                rpv_fallback = re.search(
                    r"REQUISIT[ÓOÃ]RIO\s*:?\s*([0-9A-Za-z\-]+)",
                    texto,
                    re.IGNORECASE
                )

                if rpv_fallback:
                    dados["rpv"] = (
                        rpv_fallback
                        .group(1)
                        .strip()
                    )

            # ==========================================================
            # VARA
            # ==========================================================

            vara = re.search(
                r"VARA\s*:?\s*([^\n\r]+)",
                texto,
                re.IGNORECASE
            )

            if vara:
                vara_texto = vara.group(1).strip()
                dados["vara"] = self.formatar_vara(vara_texto)

            # ==========================================================
            # BANCO
            # ==========================================================

            banco = re.search(
                r"Banco:\s*(.*?)\s*-",
                texto,
                re.IGNORECASE
            )

            if banco:
                dados["banco"] = banco.group(1).strip()

            else:

                banco_alt = re.search(
                    r"Banco:\s*([^\n\r]+)",
                    texto,
                    re.IGNORECASE
                )

                if banco_alt:
                    dados["banco"] = banco_alt.group(1).strip()

            # ==========================================================
            # DATA DA DECISÃO
            # ==========================================================

            decisao = re.search(
                r"Em\s*"
                r"(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2})"
                r"\s*\n?"
                r"Concluso para decis[ãa]o",
                texto,
                re.IGNORECASE
            )

            if decisao:
                dados["data_decisao"] = decisao.group(1).strip()

            # ==========================================================
            # DEBUG
            # ==========================================================

            print(
                f"[OK] Processo: {dados['processo']} | "
                f"RPV: {dados['rpv']} | "
                f"Vara: {dados['vara']}"
            )

            return dados

        except Exception as e:

            print(
                f"Erro ao raspar detalhes de {url}: {e}"
            )

            return {
                "link": url,
                "processo": "",
                "rpv": "",
                "vara": "",
                "banco": "",
                "data_decisao": ""
            }

    def extrair_detalhes_em_lote(self, lista_processos):
        """
        Preenche os detalhes de vários processos em paralelo.
        """

        processos_completos = []

        with ThreadPoolExecutor(
            max_workers=self.max_threads
        ) as executor:

            future_to_proc = {
                executor.submit(
                    self.extrair_detalhes_processo,
                    proc["link"]
                ): proc

                for proc in lista_processos
            }

            for future in as_completed(future_to_proc):

                proc_original = future_to_proc[future]

                try:
                    detalhes = future.result()

                    proc_original.update({
                        "processo": detalhes.get(
                            "processo",
                            ""
                        ),

                        "rpv": detalhes.get(
                            "rpv",
                            ""
                        ),

                        "vara": detalhes.get(
                            "vara",
                            ""
                        ),

                        "banco": detalhes.get(
                            "banco",
                            ""
                        ),

                        "data_decisao": detalhes.get(
                            "data_decisao",
                            ""
                        )
                    })

                    # IMPORTANTE:
                    # adiciona o processo na lista final
                    processos_completos.append(
                        proc_original
                    )

                except Exception as e:

                    print(
                        f"Erro ao processar processo: {e}"
                    )

                    processos_completos.append(
                        proc_original
                    )

        return processos_completos

    def formatar_vara(self, vara):

        if not vara:
            return ""

        vara_limpa = vara.strip().upper()

        match_numero = re.search(
            r"(\d+)\s*(ª|A|º|\.)?",
            vara_limpa
        )

        sigla_estado = ""

        for termo, sigla in ESTADOS_BRASIL.items():

            if termo in vara_limpa:
                sigla_estado = sigla
                break

        if match_numero and sigla_estado:

            numero_vara = match_numero.group(1)

            return f"{numero_vara}º VF {sigla_estado}"

        vara_formatada = re.sub(
            r"\bVARA\s+FEDERAL\s+(DE\s+)?",
            "VF ",
            vara_limpa
        )

        vara_formatada = re.sub(
            r"\bVARA\s+",
            "VF ",
            vara_formatada
        )

        return vara_formatada.strip()