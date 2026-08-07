import requests
from bs4 import BeautifulSoup
import re

ESTADOS_BRASIL = {
    # Pernambuco
    "PERNAMBUCO": "PE", 
    "RECIFE": "PE", 
    "CABO DE SANTO AGOSTINHO": "PE", 
    "CABO": "PE",
    "- PE": "PE", 
    " PE": "PE",
    
    # Alagoas
    "ALAGOAS": "AL", "MACEIÓ": "AL", "MACEIO": "AL", "- AL": "AL", " AL": "AL",
    
    # Ceará
    "CEARÁ": "CE", "CEARA": "CE", "FORTALEZA": "CE", "- CE": "CE", " CE": "CE",
    
    # Sergipe
    "SERGIPE": "SE", "ARACAJU": "SE", "- SE": "SE", " SE": "SE",
    
    # Rio Grande do Norte
    "RIO GRANDE DO NORTE": "RN", "NATAL": "RN", "- RN": "RN", " RN": "RN",
    
    # Paraíba
    "PARAÍBA": "PB", "PARAIBA": "PB", "JOÃO PESSOA": "PB", "JOAO PESSOA": "PB", "- PB": "PB", " PB": "PB"
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

        # =====================
        # VARA
        # =====================
        vara = re.search(
            r"VARA:\s*(.*)",
            texto,
            re.IGNORECASE
        )

        if vara:
            # Pega apenas a primeira linha do resultado para não puxar elementos HTML vizinhos
            nome_vara = vara.group(1).split("\n")[0].strip()
            dados["vara"] = self.formatar_vara(nome_vara)
        else:
            dados["vara"] = ""

        # =====================
        # BANCO
        # =====================
        banco = re.search(
            r"Banco:\s*(.*?)\s*-",
            texto,
            re.IGNORECASE
        )

        if banco:
            dados["banco"] = banco.group(1).strip()
        else:
            # Busca secundária caso o formato seja "Banco: Caixa Econômica Federal" sem o traço no final
            banco_alt = re.search(
                r"Banco:\s*([^\n\r]+)",
                texto,
                re.IGNORECASE
            )
            dados["banco"] = banco_alt.group(1).strip() if banco_alt else ""

        return dados


    def formatar_vara(self, vara):
        if not vara:
            return ""

        vara_limpa = vara.strip().upper()

        # 1. Extrai o número da vara (34ª, 34a, 34º, 34.)
        match_numero = re.search(r"(\d+)\s*(ª|a|º|\.)?", vara_limpa)

        # 2. Mapeia a sigla do estado via dicionário
        sigla_estado = ""
        for termo, sigla in ESTADOS_BRASIL.items():
            if termo in vara_limpa:
                sigla_estado = sigla
                break

        # Se encontrou o número e o estado/cidade, gera o padrão curto "34º VF PE"
        if match_numero and sigla_estado:
            numero_vara = match_numero.group(1)
            return f"{numero_vara}º VF {sigla_estado}"

        # Fallback para padronização geral caso não encontre no dicionário
        vara_formatada = re.sub(r"\bVARA\s+FEDERAL\s+(DE|DO|DA\s+)?", "VF ", vara_limpa)
        vara_formatada = re.sub(r"\bVARA\s+", "VF ", vara_formatada)

        return vara_formatada.strip()