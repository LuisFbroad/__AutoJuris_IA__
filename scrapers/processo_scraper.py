import requests
from bs4 import BeautifulSoup
import re


class ProcessoScraper:


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


        texto = soup.get_text(
            "\n",
            strip=True
        )


        dados = {}


        # Número processo
        processo = re.search(
            r"PROCESSO Nº (.*)",
            texto
        )

        if processo:
            dados["processo"] = processo.group(1)


        vara = re.search(
            r"VARA:\s*(.*)",
            texto
            )

        if vara:

            vara_texto = vara.group(1)

            dados["vara"] = self.formatar_vara(
                vara_texto
                )


        # Número RPV
        rpv = re.search(
            r"NÚMERO DO REQUISITÓRIO:\s*(.*)",
            texto
        )

        if rpv:
            dados["rpv"] = rpv.group(1)


        # Banco
        banco = re.search(
            r"Banco:\s*(.*?) -",
            texto
        )

        if banco:
            dados["banco"] = banco.group(1)


        # Data conclusão
        decisao = re.search(
            r"Em (\d{2}/\d{2}/\d{4} \d{2}:\d{2})\s*\nConcluso para decisão",
            texto
        )

        if decisao:
            dados["data_decisao"] = decisao.group(1)

        # Link Nº processo
        dados["link"] = url

        return dados

    def formatar_vara(self, vara):

        numero = re.search(
            r"(\d+)",
            vara
        )


        if numero:
            numero_vara = numero.group(1)
        else:
            numero_vara = ""



        if "Cear" in vara:
            estado = "CE"

        elif "Alago" in vara:
            estado = "AL"

        elif "Pernamb" in vara:
            estado = "PE"

        elif "Paraíb" in vara:
            estado = "PB"

        elif "Sergip" in vara:
            estado = "SE"

        elif "Rio Grande do Norte" in vara:
            estado = "RN"

        else:
            estado = ""



        return f"{numero_vara}º VF {estado}"


