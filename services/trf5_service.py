from scrapers.trf5_scraper import TRF5Scraper



class TRF5Service:


    def __init__(self):

        self.scraper = TRF5Scraper()



    def coletar_processos(
        self,
        limite_paginas
    ):


        processos = []



        for pagina in range(
            1,
            limite_paginas + 1
        ):


            resultado = self.scraper.buscar_pagina(
                pagina
            )



            for processo in resultado:


                detalhes = self.buscar_detalhes_processo(
                    processo["link"]
                )


                processo.update(
                    detalhes
                )


                processos.append(
                    processo
                )



        return processos





    def buscar_detalhes_processo(
        self,
        link
    ):


        return self.scraper.extrair_detalhes_processo(
            link
        )