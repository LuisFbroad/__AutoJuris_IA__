import re

import requests

from bs4 import BeautifulSoup

from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed
)


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

    def __init__(
        self,
        session=None,
        max_threads=10
    ):
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

    # ================================================================
    # EXTRAIR DETALHES DE UM PROCESSO
    # ================================================================

    def extrair_detalhes_processo(self, url):

        try:

            resposta = self.session.get(
                url,
                timeout=10
            )

            if resposta.status_code != 200:

                print(
                    f"[ERRO HTTP] {url} - "
                    f"Status: {resposta.status_code}"
                )

                return {
                    "link": url,
                    "processo": "",
                    "processo_originario": "",
                    "rpv": "",
                    "nome": "",
                    "vara": "",
                    "banco": "",
                    "data_decisao": ""
                }

            # ========================================================
            # HTML
            # ========================================================

            soup = BeautifulSoup(
                resposta.text,
                "html.parser"
            )

            texto = soup.get_text(
                "\n",
                strip=True
            )

            # ========================================================
            # DADOS
            # ========================================================

            dados = {
                "link": url,
                "processo": "",
                "processo_originario": "",
                "rpv": "",
                "nome": "",
                "vara": "",
                "banco": "",
                "data_decisao": ""
            }

            # ========================================================
            # PROCESSO ATUAL
            # ========================================================

            # Exemplo da página:
            #
            # PROCESSO Nº 0482527-54.2026.4.05.0000

            processo = re.search(
                r"PROCESSO\s*N[º°]?\s*:?\s*"
                r"(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})",
                texto,
                re.IGNORECASE
            )

            if processo:

                dados["processo"] = (
                    processo.group(1).strip()
                )

            # ========================================================
            # PROCESSO ORIGINÁRIO
            # ========================================================

            # Exemplo real da página:
            #
            # PROC. ORIGINÁRIO Nº: 00507369820254058300
            #
            # Também aceita:
            #
            # PROC. ORIGINÁRIO Nº:
            # 00507369820254058300

            processo_originario = re.search(
                r"PROC\.?\s*"
                r"ORIGIN[ÁA]RIO"
                r"\s*N[º°]?"
                r"\s*:?\s*"
                r"(\d{20})",
                texto,
                re.IGNORECASE
            )

            if processo_originario:

                dados["processo_originario"] = (
                    processo_originario
                    .group(1)
                    .strip()
                )

            # ========================================================
            # FALLBACK PROCESSO ORIGINÁRIO
            # ========================================================

            # Caso o TRF5 apresente o processo no formato CNJ:
            #
            # 0011409-02.2023.4.05.8500

            if not dados["processo_originario"]:

                processo_originario_formatado = re.search(
                    r"PROC\.?\s*"
                    r"ORIGIN[ÁA]RIO"
                    r".{0,100}?"
                    r"(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})",
                    texto,
                    re.IGNORECASE | re.DOTALL
                )

                if processo_originario_formatado:

                    dados["processo_originario"] = (
                        processo_originario_formatado
                        .group(1)
                        .strip()
                    )

            # ========================================================
            # RPV
            # ========================================================

            # Exemplos:
            #
            # RPV1234567-PE
            # RPV 1234567-PE
            # RPV1234567-AL
            # RPV3916938-SE

            rpv = re.search(
                r"\b("
                r"RPV\s*\d+\s*-\s*[A-Z]{2}"
                r")\b",
                texto,
                re.IGNORECASE
            )

            if rpv:

                dados["rpv"] = (
                    rpv.group(1)
                    .replace(" ", "")
                    .upper()
                )

            # ========================================================
            # FALLBACK RPV
            # ========================================================

            if not dados["rpv"]:

                rpv_requisicao = re.search(
                    r"REQUISI[ÇC][AÃ]O\s+DE\s+PEQUENO\s+VALOR"
                    r".{0,200}?"
                    r"\b("
                    r"RPV\s*\d+\s*-\s*[A-Z]{2}"
                    r")\b",
                    texto,
                    re.IGNORECASE | re.DOTALL
                )

                if rpv_requisicao:

                    dados["rpv"] = (
                        rpv_requisicao
                        .group(1)
                        .replace(" ", "")
                        .upper()
                    )

            # ========================================================
            # NOME / REQUERENTE
            # ========================================================

            # Exemplo real:
            #
            # REQTE : ALISSON RIBEIRO LUCENA

            nome = re.search(
                r"REQTE\s*:?\s*([^\n\r]+)",
                texto,
                re.IGNORECASE
            )

            if nome:

                nome_texto = (
                    nome.group(1)
                    .strip()
                )

                # Remove possíveis caracteres extras
                nome_texto = re.sub(
                    r"^[|:\-]+",
                    "",
                    nome_texto
                ).strip()

                dados["nome"] = nome_texto

            # ========================================================
            # FALLBACK - REQUERENTE
            # ========================================================

            if not dados["nome"]:

                requerente = re.search(
                    r"REQUERENTE\s*:?\s*([^\n\r]+)",
                    texto,
                    re.IGNORECASE
                )

                if requerente:

                    dados["nome"] = (
                        requerente
                        .group(1)
                        .strip()
                    )

            # ========================================================
            # FALLBACK - BENEFICIÁRIO
            # ========================================================

            if not dados["nome"]:

                beneficiario = re.search(
                    r"BENEFICI[ÁA]RIO\s*:?\s*([^\n\r]+)",
                    texto,
                    re.IGNORECASE
                )

                if beneficiario:

                    dados["nome"] = (
                        beneficiario
                        .group(1)
                        .strip()
                    )

            # ========================================================
            # VARA
            # ========================================================

            # Exemplo real:
            #
            # VARA: 1ª Vara Federal de Pernambuco
            # (Especializada em Naturalização)

            vara = re.search(
                r"VARA\s*:?\s*([^\n\r]+)",
                texto,
                re.IGNORECASE
            )

            if vara:

                vara_texto = (
                    vara.group(1)
                    .strip()
                )

                dados["vara"] = (
                    self.formatar_vara(
                        vara_texto
                    )
                )

            # ========================================================
            # BANCO
            # ========================================================

            banco = re.search(
                r"BANCO\s*:?\s*([^\n\r]+)",
                texto,
                re.IGNORECASE
            )

            if banco:

                dados["banco"] = (
                    banco.group(1)
                    .strip()
                )

            # ========================================================
            # DATA DA DECISÃO
            # ========================================================

            decisao = re.search(
                r"Em\s+"
                r"(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2})"
                r".{0,100}?"
                r"Concluso\s+para\s+decis[ãa]o",
                texto,
                re.IGNORECASE | re.DOTALL
            )

            if decisao:

                dados["data_decisao"] = (
                    decisao.group(1)
                    .strip()
                )

            # ========================================================
            # DEBUG
            # ========================================================

            print(
                "[OK] "
                f"Processo: {dados['processo']} | "
                f"Originário: {dados['processo_originario']} | "
                f"RPV: {dados['rpv']} | "
                f"Nome: {dados['nome']} | "
                f"Vara: {dados['vara']} | "
                f"Banco: {dados['banco']}"
            )

            return dados

        except Exception as e:

            print(
                f"[ERRO] Ao raspar detalhes de "
                f"{url}: {e}"
            )

            return {
                "link": url,
                "processo": "",
                "processo_originario": "",
                "rpv": "",
                "nome": "",
                "vara": "",
                "banco": "",
                "data_decisao": ""
            }

    # ================================================================
    # EXTRAIR DETALHES EM LOTE
    # ================================================================

    def extrair_detalhes_em_lote(
        self,
        lista_processos
    ):

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

            for future in as_completed(
                future_to_proc
            ):

                proc_original = (
                    future_to_proc[future]
                )

                try:

                    detalhes = future.result()

                    # =================================================
                    # ATUALIZA OS DADOS DO PROCESSO
                    # =================================================

                    proc_original.update({

                        "processo": detalhes.get(
                            "processo",
                            ""
                        ),

                        "processo_originario": detalhes.get(
                            "processo_originario",
                            ""
                        ),

                        "rpv": detalhes.get(
                            "rpv",
                            ""
                        ),

                        "nome": detalhes.get(
                            "nome",
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

                    processos_completos.append(
                        proc_original
                    )

                except Exception as e:

                    print(
                        "[ERRO] Ao processar "
                        f"processo: {e}"
                    )

                    processos_completos.append(
                        proc_original
                    )

        return processos_completos

    # ================================================================
    # FORMATAR VARA
    # ================================================================

    def formatar_vara(
        self,
        vara
    ):

        if not vara:
            return ""

        vara_limpa = (
            vara
            .strip()
            .upper()
        )

        # ============================================================
        # NÚMERO DA VARA
        # ============================================================

        match_numero = re.search(
            r"(\d+)\s*(?:ª|A|º|\.)?",
            vara_limpa
        )

        # ============================================================
        # ESTADO
        # ============================================================

        sigla_estado = ""

        for termo, sigla in ESTADOS_BRASIL.items():

            if termo in vara_limpa:

                sigla_estado = sigla

                break

        # ============================================================
        # FORMATO PADRÃO
        # ============================================================

        if match_numero and sigla_estado:

            numero_vara = (
                match_numero.group(1)
            )

            return (
                f"{numero_vara}º VF "
                f"{sigla_estado}"
            )

        # ============================================================
        # FALLBACK
        # ============================================================

        vara_formatada = re.sub(
            r"\bVARA\s+FEDERAL\s+DE\s+",
            "VF ",
            vara_limpa
        )

        vara_formatada = re.sub(
            r"\bVARA\s+",
            "VF ",
            vara_formatada
        )

        return vara_formatada.strip()