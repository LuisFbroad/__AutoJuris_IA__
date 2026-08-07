import requests
from bs4 import BeautifulSoup
import re
from scrapers.trf5_scraper import ESTADOS_BRASIL


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
        if not vara:
            return ""

        vara_limpa = vara.strip().upper()

        # 1. Tenta extrair o número da vara (funciona para 33ª, 33a, 33º, 33. ou apenas 33)
        match_numero = re.search(r"(\d+)\s*(ª|a|º|\.)?", vara_limpa)
        
        # 2. Procura a sigla do estado no texto
        sigla_estado = ""
        for termo, sigla in ESTADOS_BRASIL.items():
            if termo in vara_limpa:
                sigla_estado = sigla
                break

        # Se encontrou tanto o número quanto o estado, retorna o padrão limpo: "33º VF PE"
        if match_numero and sigla_estado:
            numero_vara = match_numero.group(1)
            return f"{numero_vara}º VF {sigla_estado}"

        # Caso não ache o padrão exato, remove termos pesados mantendo a legibilidade
        vara_formatada = re.sub(r"\bVARA\s+FEDERAL\s+(DE\s+)?", "VF ", vara_limpa)
        vara_formatada = re.sub(r"\bVARA\s+", "VF ", vara_formatada)
        
        return vara_formatada.strip()