import re


class DadosExtractor:

    def extrair(self, soup, texto):

        dados = {
            "nome": "",
            "vara": "",
            "banco": "",
            "data_decisao": "",
        }

        dados["nome"] = self._extrair_nome(
            soup,
            texto
        )

        dados["vara"] = self._extrair_campo(
            texto,
            [
                r"VARA\s*:?\s*([^\n\r]+)"
            ]
        )

        dados["banco"] = self._extrair_campo(
            texto,
            [
                r"BANCO\s*:?\s*([^\n\r]+)"
            ]
        )

        dados["data_decisao"] = (
            self._extrair_data_decisao(
                texto
            )
        )

        return dados

    # =========================================================
    # NOME
    # =========================================================

    def _extrair_nome(self, soup, texto):

        padroes = [
            r"REQTE\s*:?\s*([^\n\r]+)",
            r"REQUERENTE\s*:?\s*([^\n\r]+)",
            r"BENEFICI[ÁA]RIO\s*:?\s*([^\n\r]+)"
        ]

        for padrao in padroes:

            match = re.search(
                padrao,
                texto,
                re.IGNORECASE
            )

            if match:

                nome = match.group(1)

                nome = re.sub(
                    r"^[|:\-]+",
                    "",
                    nome
                )

                return nome.strip()

        return ""

    # =========================================================
    # CAMPOS SIMPLES
    # =========================================================

    def _extrair_campo(
        self,
        texto,
        padroes
    ):

        for padrao in padroes:

            match = re.search(
                padrao,
                texto,
                re.IGNORECASE
            )

            if match:
                return match.group(1).strip()

        return ""

    # =========================================================
    # DATA DA DECISÃO
    # =========================================================

    def _extrair_data_decisao(
        self,
        texto
    ):

        match = re.search(
            r"Em\s+"
            r"(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2})"
            r".{0,150}?"
            r"Concluso\s+para\s+decis[ãa]o",
            texto,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            return match.group(1).strip()

        return ""