import re


class ProcessoExtractor:
    """
    Extrator especializado em números de processos.

    Prioridade:
    1. Campo/estrutura HTML
    2. Texto próximo ao marcador
    3. Regex global como fallback
    """

    PADRAO_CNJ = re.compile(
        r"\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b"
    )

    PADRAO_CNJ_SEM_FORMATACAO = re.compile(
        r"\b\d{20}\b"
    )

    def extrair(self, soup, texto):
        resultado = {
            "processo": "",
            "processo_originario": "",
            "origem_processo": "",
        }

        # =====================================================
        # PROCESSO ATUAL
        # =====================================================

        processo = self._extrair_processo_atual(
            soup,
            texto
        )

        if processo:
            resultado["processo"] = processo
            resultado["origem_processo"] = "html/regex"

        # =====================================================
        # PROCESSO ORIGINÁRIO
        # =====================================================

        originario = self._extrair_originario(
            soup,
            texto
        )

        if originario:
            resultado["processo_originario"] = originario

        return resultado

    # =========================================================
    # PROCESSO ATUAL
    # =========================================================

    def _extrair_processo_atual(self, soup, texto):

        # Primeiro tenta encontrar o campo específico.

        for elemento in soup.find_all(
            string=re.compile(
                r"PROCESSO\s*N[º°]?",
                re.IGNORECASE
            )
        ):
            pai = elemento.parent

            if not pai:
                continue

            texto_pai = pai.get_text(
                " ",
                strip=True
            )

            match = self.PADRAO_CNJ.search(
                texto_pai
            )

            if match:
                return match.group(0)

        # =====================================================
        # FALLBACK REGEX
        # =====================================================

        match = re.search(
            r"PROCESSO\s*N[º°]?\s*:?\s*"
            r"(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})",
            texto,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

        return ""

    # =========================================================
    # PROCESSO ORIGINÁRIO
    # =========================================================

    def _extrair_originario(self, soup, texto):

        marcador = re.compile(
            r"PROC\.?\s*ORIGIN[ÁA]RIO",
            re.IGNORECASE
        )

        # =====================================================
        # TENTA ENCONTRAR O CAMPO NO HTML
        # =====================================================

        elemento = soup.find(
            string=marcador
        )

        if elemento:

            pai = elemento.parent

            if pai:

                texto_pai = pai.parent.get_text(
                    " ",
                    strip=True
                ) if pai.parent else pai.get_text(
                    " ",
                    strip=True
                )

                # Formato CNJ
                match = self.PADRAO_CNJ.search(
                    texto_pai
                )

                if match:
                    return match.group(0)

                # Formato 20 dígitos
                match = self.PADRAO_CNJ_SEM_FORMATACAO.search(
                    texto_pai
                )

                if match:
                    return match.group(0)

        # =====================================================
        # REGEX FORMATO 20 DÍGITOS
        # =====================================================

        match = re.search(
            r"PROC\.?\s*"
            r"ORIGIN[ÁA]RIO"
            r"\s*N[º°]?"
            r"\s*:?\s*"
            r"(\d{20})",
            texto,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

        # =====================================================
        # FALLBACK CNJ
        # =====================================================

        match = re.search(
            r"PROC\.?\s*"
            r"ORIGIN[ÁA]RIO"
            r".{0,150}?"
            r"(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})",
            texto,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            return match.group(1)

        return ""