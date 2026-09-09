import os
import re
import requests

from bs4 import BeautifulSoup

from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed
)

from scrapers.extractors.processo_extractor import (
    ProcessoExtractor
)

from scrapers.extractors.rpv_extractor import (
    RPVExtractor
)

from scrapers.extractors.dados_extractor import (
    DadosExtractor
)

from validators.processo_validator import (
    ProcessoValidator
)


ESTADOS_BRASIL = {
    "PERNAMBUCO": "PE",
    "RECIFE": "PE",
    "CABO DE SANTO AGOSTINHO": "PE",
    "CABO": "PE",

    "ALAGOAS": "AL",
    "MACEIÓ": "AL",
    "MACEIO": "AL",

    "CEARÁ": "CE",
    "CEARA": "CE",
    "FORTALEZA": "CE",

    "SERGIPE": "SE",
    "ARACAJU": "SE",

    "RIO GRANDE DO NORTE": "RN",
    "NATAL": "RN",

    "PARAÍBA": "PB",
    "PARAIBA": "PB",
    "JOÃO PESSOA": "PB",
    "JOAO PESSOA": "PB"
}


class ProcessoScraper:

    def __init__(
        self,
        session=None,
        max_threads=10,
        salvar_html=False,
        diretorio_html="dados/bruto"
    ):

        self.session = (
            session
            or requests.Session()
        )

        self.max_threads = max_threads

        self.salvar_html = salvar_html

        self.diretorio_html = (
            diretorio_html
        )

        if "User-Agent" not in self.session.headers:

            self.session.headers.update({
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/151.0.0.0 "
                    "Safari/537.36"
                )
            })

        # =====================================================
        # EXTRACTORS
        # =====================================================

        self.processo_extractor = (
            ProcessoExtractor()
        )

        self.rpv_extractor = (
            RPVExtractor()
        )

        self.dados_extractor = (
            DadosExtractor()
        )

    # =========================================================
    # EXTRAIR DETALHES
    # =========================================================

    def extrair_detalhes_processo(
        self,
        url
    ):

        dados = self._dados_vazios(url)

        try:

            resposta = self.session.get(
                url,
                timeout=20
            )

            resposta.raise_for_status()

            # =================================================
            # SALVAR HTML
            # =================================================

            if self.salvar_html:

                self._salvar_html(
                    url,
                    resposta.text
                )

            # =================================================
            # BEAUTIFULSOUP
            # =================================================

            soup = BeautifulSoup(
                resposta.text,
                "html.parser"
            )

            texto = soup.get_text(
                "\n",
                strip=True
            )

            # =================================================
            # PROCESSO
            # =================================================

            processo = (
                self.processo_extractor.extrair(
                    soup,
                    texto
                )
            )

            dados.update(
                processo
            )

            # =================================================
            # RPV
            # =================================================

            rpv = (
                self.rpv_extractor.extrair(
                    soup,
                    texto
                )
            )

            dados.update(
                rpv
            )

            # =================================================
            # DEMAIS DADOS
            # =================================================

            outros = (
                self.dados_extractor.extrair(
                    soup,
                    texto
                )
            )

            dados.update(
                outros
            )

            # =================================================
            # VARA FORMATADA
            # =================================================

            if dados.get("vara"):

                dados["vara"] = (
                    self.formatar_vara(
                        dados["vara"]
                    )
                )

            # =================================================
            # VALIDAÇÃO
            # =================================================

            dados["processo_valido"] = (
                ProcessoValidator.validar_processo(
                    dados.get("processo")
                )
            )

            dados["rpv_valida"] = (
                ProcessoValidator.validar_rpv(
                    dados.get("rpv")
                )
            )

            dados["nome_valido"] = (
                ProcessoValidator.validar_nome(
                    dados.get("nome")
                )
            )

            # =================================================
            # CONFIANÇA
            # =================================================

            dados["confianca"] = (
                ProcessoValidator.calcular_confianca(
                    dados
                )
            )

            # =================================================
            # CLASSIFICAÇÃO
            # =================================================

            dados["nivel_confianca"] = (
                self.classificar_confianca(
                    dados["confianca"]
                )
            )

            print(
                "[OK] "
                f"{dados.get('processo', '')} | "
                f"{dados.get('rpv', '')} | "
                f"{dados.get('nome', '')} | "
                f"Confiança: "
                f"{dados.get('confianca', 0):.0%}"
            )

            return dados

        except Exception as e:

            print(
                "[ERRO] "
                f"{url}: {e}"
            )

            dados["erro"] = str(e)

            return dados

    # =========================================================
    # DADOS VAZIOS
    # =========================================================

    @staticmethod
    def _dados_vazios(url):

        return {
            "link": url,

            "processo": "",
            "processo_originario": "",

            "rpv": "",
            "nome": "",

            "vara": "",
            "banco": "",

            "data_decisao": "",

            "data_movimento": "",
            "hora_movimento": "",

            "situacao": "",

            "origem_processo": "",
            "origem_rpv": "",

            "processo_valido": False,
            "rpv_valida": False,
            "nome_valido": False,

            "confianca": 0.0,
            "nivel_confianca": "BAIXA",

            "erro": ""
        }

    # =========================================================
    # CLASSIFICAR CONFIANÇA
    # =========================================================

    @staticmethod
    def classificar_confianca(
        confianca
    ):

        if confianca >= 0.90:
            return "ALTA"

        if confianca >= 0.70:
            return "MÉDIA"

        return "BAIXA"

    # =========================================================
    # EXTRAÇÃO EM LOTE
    # =========================================================

    def extrair_detalhes_em_lote(
        self,
        lista_processos
    ):

        processos_completos = []

        if not lista_processos:
            return []

        with ThreadPoolExecutor(
            max_workers=self.max_threads
        ) as executor:

            futuros = {
                executor.submit(
                    self.extrair_detalhes_processo,
                    processo.get("link", "")
                ): processo

                for processo in lista_processos
                if processo.get("link")
            }

            for futuro in as_completed(
                futuros
            ):

                processo_original = (
                    futuros[futuro]
                )

                try:

                    detalhes = (
                        futuro.result()
                    )

                    # Mantém dados da listagem
                    # caso a página de detalhes
                    # não contenha algum deles.

                    for campo in [
                        "processo",
                        "rpv",
                        "data_movimento",
                        "hora_movimento",
                        "situacao",
                        "link"
                    ]:

                        if not detalhes.get(campo):

                            detalhes[campo] = (
                                processo_original.get(
                                    campo,
                                    ""
                                )
                            )

                    processo_original.update(
                        detalhes
                    )

                    processos_completos.append(
                        processo_original
                    )

                except Exception as e:

                    print(
                        "[ERRO] "
                        f"Processo: {e}"
                    )

                    processos_completos.append(
                        processo_original
                    )

        return processos_completos

    # =========================================================
    # SALVAR HTML
    # =========================================================

    def _salvar_html(
        self,
        url,
        html
    ):

        try:

            os.makedirs(
                self.diretorio_html,
                exist_ok=True
            )

            processo = self._extrair_id_url(
                url
            )

            if not processo:

                processo = "pagina"

            caminho = os.path.join(
                self.diretorio_html,
                f"{processo}.html"
            )

            with open(
                caminho,
                "w",
                encoding="utf-8"
            ) as arquivo:

                arquivo.write(
                    html
                )

        except Exception as e:

            print(
                "[AVISO] "
                f"Não foi possível salvar HTML: {e}"
            )

    # =========================================================
    # IDENTIFICAR ID
    # =========================================================

    @staticmethod
    def _extrair_id_url(url):

        match = re.search(
            r"(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})",
            url
        )

        if match:
            return (
                match.group(1)
                .replace(".", "_")
                .replace("-", "_")
            )

        return ""

    # =========================================================
    # FORMATAR VARA
    # =========================================================

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

        numero = ""

        match_numero = re.search(
            r"(\d+)\s*(?:ª|A|º|\.)?",
            vara_limpa
        )

        if match_numero:

            numero = (
                match_numero.group(1)
            )

        estado = ""

        for termo, sigla in (
            ESTADOS_BRASIL.items()
        ):

            if termo in vara_limpa:

                estado = sigla
                break

        if numero and estado:

            return (
                f"{numero}ª VARA FEDERAL - "
                f"{estado}"
            )

        if estado:

            return estado

        return vara.strip()