import re
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

ESTADOS_BRASIL = {
    "PERNAMBUCO": "PE", "RECIFE": "PE", "CABO DE SANTO AGOSTINHO": "PE", "CABO": "PE", "- PE": "PE", " PE": "PE",
    "ALAGOAS": "AL", "MACEIÓ": "AL", "MACEIO": "AL", "- AL": "AL", " AL": "AL",
    "CEARÁ": "CE", "CEARA": "CE", "FORTALEZA": "CE", "- CE": "CE", " CE": "CE",
    "SERGIPE": "SE", "ARACAJU": "SE", "- SE": "SE", " SE": "SE",
    "RIO GRANDE DO NORTE": "RN", "NATAL": "RN", "- RN": "RN", " RN": "RN",
    "PARAÍBA": "PB", "PARAIBA": "PB", "JOÃO PESSOA": "PB", "JOAO PESSOA": "PB", "- PB": "PB", " PB": "PB"
}


class ProcessoScraper:

    def __init__(self, session=None, max_threads=10):
        # Utiliza a sessão do TRF5Scraper ou cria uma nova persistente
        self.session = session or requests.Session()
        self.max_threads = max_threads

        if "User-Agent" not in self.session.headers:
            self.session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })

    def extrair_detalhes_processo(self, url):
        """Extrai os detalhes (Vara, Banco, Data) de um único processo."""
        try:
            resposta = self.session.get(url, timeout=10)
            if resposta.status_code != 200:
                return {"link": url, "vara": "", "banco": "", "data_decisao": ""}

            soup = BeautifulSoup(resposta.text, "html.parser")
            texto = soup.get_text("\n", strip=True)

            dados = {"link": url}

            # Número processo
            processo = re.search(r"PROCESSO Nº\s*(.*)", texto, re.IGNORECASE)
            if processo:
                dados["processo"] = processo.group(1).split("\n")[0].strip()

            # Vara
            vara = re.search(r"VARA:\s*(.*)", texto, re.IGNORECASE)
            if vara:
                vara_texto = vara.group(1).split("\n")[0].strip()
                dados["vara"] = self.formatar_vara(vara_texto)
            else:
                dados["vara"] = ""

            # Número RPV
            rpv = re.search(r"NÚMERO DO REQUISITÓRIO:\s*(.*)", texto, re.IGNORECASE)
            if rpv:
                dados["rpv"] = rpv.group(1).split("\n")[0].strip()

            # Banco (Busca primária com traço e fallback)
            banco = re.search(r"Banco:\s*(.*?)\s*-", texto, re.IGNORECASE)
            if banco:
                dados["banco"] = banco.group(1).strip()
            else:
                banco_alt = re.search(r"Banco:\s*([^\n\r]+)", texto, re.IGNORECASE)
                dados["banco"] = banco_alt.group(1).strip() if banco_alt else ""

            # Data conclusão
            decisao = re.search(
                r"Em\s*(\d{2}/\d{2}/\d{4}\s*\d{2}:\d{2})\s*\n?Concluso para decisão",
                texto,
                re.IGNORECASE
            )
            if decisao:
                dados["data_decisao"] = decisao.group(1)

            return dados

        except Exception as e:
            print(f"⚠️ Erro ao raspar detalhes de {url}: {e}")
            return {"link": url, "vara": "", "banco": "", "data_decisao": ""}

    def extrair_detalhes_em_lote(self, lista_processos):
        """Otimização de velocidade: Preenche os detalhes de vários processos em paralelo."""
        processos_completos = []

        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            # Mapeia cada futuro ao dicionário original do processo
            future_to_proc = {
                executor.submit(self.extrair_detalhes_processo, proc["link"]): proc
                for proc in lista_processos
            }

            for future in as_completed(future_to_proc):
                proc_original = future_to_proc[future]
                detalhes = future.result()

                # Mescla os detalhes obtidos de volta no dicionário do processo
                proc_original.update({
                    "vara": detalhes.get("vara", ""),
                    "banco": detalhes.get("banco", ""),
                    "data_decisao": detalhes.get("data_decisao", "")
                })
                processos_completos.append(proc_original)

        return processos_completos

    def formatar_vara(self, vara):
        if not vara:
            return ""

        vara_limpa = vara.strip().upper()
        match_numero = re.search(r"(\d+)\s*(ª|a|º|\.)?", vara_limpa)

        sigla_estado = ""
        for termo, sigla in ESTADOS_BRASIL.items():
            if termo in vara_limpa:
                sigla_estado = sigla
                break

        if match_numero and sigla_estado:
            numero_vara = match_numero.group(1)
            return f"{numero_vara}º VF {sigla_estado}"

        vara_formatada = re.sub(r"\bVARA\s+FEDERAL\s+(DE\s+)?", "VF ", vara_limpa)
        vara_formatada = re.sub(r"\bVARA\s+", "VF ", vara_formatada)

        return vara_formatada.strip()