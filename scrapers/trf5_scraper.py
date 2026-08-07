import requests
from bs4 import BeautifulSoup
import re

ESTADOS_BRASIL = {

    "ALAGOAS": "AL",

    "CEARÁ": "CE",
    "CEARA": "CE",

    "SERGIPE": "SE",

    "RIO GRANDE DO NORTE": "RN",

    "PERNAMBUCO": "PE",

    "PARAÍBA": "PB",
    "PARAIBA": "PB"

}

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


        print("==============================")
        print("ACESSANDO:")
        print(url)
        print("==============================")


        resposta = requests.get(
            url,
            headers={
                "User-Agent":"Mozilla/5.0"
            }
        )


        print("STATUS:", resposta.status_code)


        soup = BeautifulSoup(
            resposta.text,
            "html.parser"
        )


        return self.extrair_processos(soup)




    def extrair_processos(self, soup):


        processos = []

        encontrados = set()



        tabelas = soup.find_all(
            "table"
        )


        for tabela in tabelas:


            linhas = tabela.find_all(
                "tr"
            )



            for linha in linhas:


                colunas = linha.find_all(
                    "td"
                )


                if len(colunas) < 3:
                    continue



                texto = " ".join(
                    coluna.get_text(
                        " ",
                        strip=True
                    )
                    for coluna in colunas
                )



                processo = re.search(
                    r"\d{7}-\d{2}\.\d{4}\.4\.05\.\d{4}",
                    texto
                )


                if not processo:
                    continue



                numero = processo.group()



                if numero in encontrados:
                    continue



                encontrados.add(numero)



                # =====================
                # PEGAR RPV
                # =====================


                rpv = re.search(
                    r"RPV\d+-[A-Z]{2}",
                    texto
                )


                numero_rpv = ""


                if rpv:

                    numero_rpv = rpv.group()



                # =====================
                # LINK PROCESSO
                # =====================


                link = (
                    f"{self.base_url}/processo/{numero}"
                )



                dados = {

                    "numero": numero,

                    "rpv": numero_rpv,

                    "link": link

                }



                print(
                    "PROCESSO:",
                    dados
                )



                processos.append(
                    dados
                )



        return processos







    def extrair_detalhes_processo(
        self,
        url
    ):



        resposta = requests.get(
            url,
            headers={
                "User-Agent":"Mozilla/5.0"
            }
        )


        soup = BeautifulSoup(
            resposta.text,
            "html.parser"
        )


        texto = soup.get_text(
            "\n",
            strip=True
        )



        dados = {}



        # =====================
        # VARA
        # =====================


        vara = re.search(
            r"VARA:\s*(.*)",
            texto,
            re.IGNORECASE
        )


        if vara:


            dados["vara"] = self.formatar_vara(
                vara.group(1)
            )


        else:


            dados["vara"] = ""





        # =====================
        # BANCO
        # =====================


        banco = re.search(
            r"Banco:\s*(.*?)\s*-",
            texto
        )



        if banco:


            dados["banco"] = banco.group(1).strip()


        else:


            dados["banco"] = ""



        return dados






    def formatar_vara(
        self,
        vara
    ):


        vara = vara.upper()



        # pega número da vara
        numero = re.search(
            r"(\d+)ª",
            vara
        )


        if not numero:

            return vara[:20]



        numero_vara = numero.group(1)



        sigla_estado = ""



        # procura o estado
        for estado, sigla in ESTADOS_BRASIL.items():


            if estado in vara:

                sigla_estado = sigla

                break



        if sigla_estado:


            return f"{numero_vara}º VF {sigla_estado}"



        return vara[:20]