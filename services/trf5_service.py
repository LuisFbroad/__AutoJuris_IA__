from scrapers.trf5_scraper import TRF5Scraper
from scrapers.processo_scraper import ProcessoScraper


class TRF5Service:

    def __init__(self):

        self.scraper = TRF5Scraper()

        self.processo_scraper = ProcessoScraper()

    def coletar_processos(
        self,
        limite_paginas
    ):

        processos = []

        for pagina in range(
            1,
            limite_paginas + 1
        ):

            print(
                f"\n[TRF5] Coletando página {pagina}..."
            )

            try:

                resultado = self.scraper.buscar_pagina(
                    pagina
                )

                processos.extend(
                    resultado
                )

            except Exception as e:

                print(
                    f"[ERRO] Página {pagina}: {e}"
                )

        return processos

    def buscar_detalhes_processo(
        self,
        link
    ):

        return (
            self.processo_scraper
            .extrair_detalhes_processo(
                link
            )
        )