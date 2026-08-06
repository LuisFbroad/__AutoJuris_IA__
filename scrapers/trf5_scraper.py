import requests
from bs4 import BeautifulSoup


class TRF5Scraper:


    def __init__(self):

        self.base_url = "https://cp.trf5.jus.br"



    def buscar_pagina(self, pagina):

        url = (
            "https://cp.trf5.jus.br/processo/rpvprec/"
            "filtroRPVPrec/cpfcnpj/porData/"
            "tiporpv/ativos/vinculados/"
            "17391998000103//"
            f"{pagina}"
        )


        resposta = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )


        soup = BeautifulSoup(
            resposta.text,
            "html.parser"
        )


        return self.extrair_processos(soup)



    def extrair_processos(self, soup):

        lista = []


        links = soup.find_all(
            "a",
            class_="linkar"
        )


        for link in links:

            href = link.get("href")


            if href and "/processo/" in href:

                lista.append(
                    {
                        "numero": link.text.strip(),
                        "link": self.base_url + href
                    }
                )


        return lista



    # NOVA FUNÇÃO
    def extrair_detalhes_processo(self, url):


        resposta = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )


        soup = BeautifulSoup(
            resposta.text,
            "html.parser"
        )


        dados = {}


        dados["titulo"] = soup.title.text.strip()


        # Aqui vamos procurar as tabelas
        tabelas = soup.find_all("table")


        for tabela in tabelas:

            texto = tabela.text.strip()


            if "RPV" in texto:

                dados["conteudo_rpv"] = texto


        return dados