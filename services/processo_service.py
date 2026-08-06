from scrapers.processo_scraper import ProcessoScraper


class ProcessoService:


    def __init__(self):

        self.scraper = ProcessoScraper()



    def coletar_detalhes(self, processos):

        resultado = []


        for processo in processos:

            dados = self.scraper.extrair_dados(
                processo["link"]
            )

            resultado.append(dados)


        return resultado