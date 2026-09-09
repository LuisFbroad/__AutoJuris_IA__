import re


class RPVExtractor:

    PADRAO_RPV = re.compile(
        r"\bRPV\s*\d+\s*-\s*[A-Z]{2}\b",
        re.IGNORECASE
    )

    def extrair(self, soup, texto):

        # =====================================================
        # PRIMEIRA TENTATIVA
        # PROCURA CAMPOS RELACIONADOS À RPV
        # =====================================================

        marcadores = [
            "RPV",
            "REQUISIÇÃO DE PEQUENO VALOR",
            "REQUISICAO DE PEQUENO VALOR"
        ]

        for marcador in marcadores:

            elemento = soup.find(
                string=re.compile(
                    re.escape(marcador),
                    re.IGNORECASE
                )
            )

            if not elemento:
                continue

            pai = elemento.parent

            if not pai:
                continue

            # Procura alguns níveis acima
            atual = pai

            for _ in range(5):

                if not atual:
                    break

                texto_pai = atual.get_text(
                    " ",
                    strip=True
                )

                match = self.PADRAO_RPV.search(
                    texto_pai
                )

                if match:
                    return {
                        "rpv": self._normalizar(
                            match.group(0)
                        ),
                        "origem_rpv": "html"
                    }

                atual = atual.parent

        # =====================================================
        # REGEX GLOBAL
        # =====================================================

        match = self.PADRAO_RPV.search(
            texto
        )

        if match:
            return {
                "rpv": self._normalizar(
                    match.group(0)
                ),
                "origem_rpv": "regex"
            }

        # =====================================================
        # FALLBACK ESPECÍFICO
        # =====================================================

        match = re.search(
            r"REQUISI[ÇC][AÃ]O\s+DE\s+PEQUENO\s+VALOR"
            r".{0,300}?"
            r"(RPV\s*\d+\s*-\s*[A-Z]{2})",
            texto,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            return {
                "rpv": self._normalizar(
                    match.group(1)
                ),
                "origem_rpv": "fallback"
            }

        return {
            "rpv": "",
            "origem_rpv": ""
        }

    @staticmethod
    def _normalizar(valor):

        return (
            valor
            .replace(" ", "")
            .upper()
            .strip()
        )