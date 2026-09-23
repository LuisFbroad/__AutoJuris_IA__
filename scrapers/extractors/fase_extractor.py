import re

class FaseExtractor:

    def extrair(self, soup, texto):

        fase = ""

        padroes = [
            r"Fase\s*Atual\s*[:\-]?\s*(.+)",
            r"Fase\s*[:\-]?\s*(.+)",
            r"Situação\s*Atual\s*[:\-]?\s*(.+)",
            r"Situação\s*[:\-]?\s*(.+)"
        ]

        for padrao in padroes:

            match = re.search(
                padrao,
                texto,
                re.IGNORECASE
            )

            if match:

                fase = match.group(1).strip()

                fase = re.sub(
                    r"\s+",
                    " ",
                    fase
                )

                return fase

        return ""
