from scrapers.trf5_scraper import TRF5Scraper



class TRF5Service:


    def __init__(self):

        self.scraper = TRF5Scraper()



    def coletar_processos(
        self,
        limite_paginas
    ):


        processos = []


        for pagina in range(1, limite_paginas + 1):


            resultado = self.scraper.buscar_pagina(
                pagina
            )


            processos.extend(
                resultado
            )


        return processos



    def buscar_detalhes(
        self,
        link
    ):


        return self.scraper.extrair_detalhes_processo(
            link
        )