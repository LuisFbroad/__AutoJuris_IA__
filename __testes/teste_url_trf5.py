import os
import re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv


# ============================================================
# CONFIGURAÇÃO
# ============================================================

load_dotenv()

DOCUMENTO = "89957709291"

BASE_URL = os.getenv(
    "TRF5_BASE_URL",
    "https://cp.trf5.jus.br"
)

URL = (
    f"{BASE_URL}/processo/rpvprec/"
    f"filtroRPVPrec/cpfcnpj/porData/"
    f"tiporpv/ativos/vinculados/"
    f"{DOCUMENTO}//1"
)


# ============================================================
# CABEÇALHO
# ============================================================

print("=" * 70)
print("TESTE DE ESTRUTURA DA LISTAGEM TRF5")
print("=" * 70)

print()
print("Documento:", DOCUMENTO)
print("URL:")
print(URL)

print()
print("=" * 70)
print("ACESSANDO TRF5")
print("=" * 70)


# ============================================================
# SESSÃO
# ============================================================

session = requests.Session()

session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/avif,"
        "image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
})


# ============================================================
# REQUEST
# ============================================================

try:

    resposta = session.get(
        URL,
        timeout=30
    )

    print()
    print("Status:", resposta.status_code)
    print("URL final:", resposta.url)
    print("Tamanho:", len(resposta.content), "bytes")
    print("Encoding:", resposta.encoding)
    print("Content-Type:",
          resposta.headers.get("Content-Type"))

except Exception as e:

    print()
    print("=" * 70)
    print("ERRO NA REQUISIÇÃO")
    print("=" * 70)
    print(e)

    raise SystemExit(1)


# ============================================================
# SALVAR HTML
# ============================================================

arquivo_html = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "trf5_resposta.html"
)

with open(
    arquivo_html,
    "w",
    encoding="utf-8"
) as arquivo:

    arquivo.write(resposta.text)


print()
print("HTML salvo em:")
print(arquivo_html)


# ============================================================
# BEAUTIFULSOUP
# ============================================================

soup = BeautifulSoup(
    resposta.text,
    "html.parser"
)


# ============================================================
# TABELAS
# ============================================================

tabelas = soup.find_all("table")

print()
print("=" * 70)
print("ESTRUTURA HTML")
print("=" * 70)

print()
print("Quantidade de tabelas:", len(tabelas))


for indice, tabela in enumerate(tabelas, start=1):

    linhas = tabela.find_all("tr")

    print(
        f"Tabela {indice}: "
        f"{len(linhas)} linhas"
    )


# ============================================================
# LINKS
# ============================================================

links = soup.find_all("a")

print()
print("=" * 70)
print("LINKS ENCONTRADOS")
print("=" * 70)

print()
print("Quantidade de links:", len(links))


contador = 0

for link in links:

    href = link.get("href", "")
    texto = link.get_text(" ", strip=True)

    if (
        "processo" in href.lower()
        or "rpv" in href.lower()
        or "prec" in href.lower()
    ):

        contador += 1

        print()
        print(f"[LINK {contador}]")
        print("Texto:", texto)
        print("HREF :", href)


# ============================================================
# NÚMEROS DE PROCESSO
# ============================================================

texto_completo = soup.get_text(
    " ",
    strip=True
)

padrao_processo = re.compile(
    r"\b\d{7}-\d{2}\.\d{4}\.\d\.05\.\d{4}\b"
)

processos = padrao_processo.findall(
    texto_completo
)

processos_unicos = list(
    dict.fromkeys(processos)
)


print()
print("=" * 70)
print("NÚMEROS DE PROCESSO")
print("=" * 70)

print()
print(
    "Processos encontrados:",
    len(processos_unicos)
)


for processo in processos_unicos:

    print(
        " -",
        processo
    )


# ============================================================
# PROCURA POR RPV
# ============================================================

padrao_rpv = re.compile(
    r"\bRPV\s*\d*\s*-?\s*[A-Z]{2}\b",
    re.IGNORECASE
)

rpvs = padrao_rpv.findall(
    texto_completo
)

rpvs_unicos = list(
    dict.fromkeys(
        rpv.replace(" ", "").upper()
        for rpv in rpvs
    )
)


print()
print("=" * 70)
print("RPVs")
print("=" * 70)

print()
print(
    "RPVs encontrados:",
    len(rpvs_unicos)
)


for rpv in rpvs_unicos:

    print(
        " -",
        rpv
    )


# ============================================================
# LINHAS DAS TABELAS
# ============================================================

print()
print("=" * 70)
print("LINHAS COM PROCESSOS")
print("=" * 70)

linhas_com_processo = 0

for tabela_indice, tabela in enumerate(
    tabelas,
    start=1
):

    linhas = tabela.find_all("tr")

    for linha_indice, linha in enumerate(
        linhas,
        start=1
    ):

        texto_linha = linha.get_text(
            " ",
            strip=True
        )

        if padrao_processo.search(
            texto_linha
        ):

            linhas_com_processo += 1

            print()
            print(
                f"[Tabela {tabela_indice} "
                f"/ Linha {linha_indice}]"
            )

            print(
                texto_linha
            )


print()
print(
    "Linhas contendo processo:",
    linhas_com_processo
)


# ============================================================
# RESUMO
# ============================================================

print()
print("=" * 70)
print("RESUMO")
print("=" * 70)

print()
print("Status HTTP       :", resposta.status_code)
print("Tamanho HTML      :", len(resposta.content))
print("Tabelas           :", len(tabelas))
print("Links             :", len(links))
print("Processos         :", len(processos_unicos))
print("RPVs              :", len(rpvs_unicos))
print("Linhas c/processo :", linhas_com_processo)

print()
print("=" * 70)
print("TESTE FINALIZADO")
print("=" * 70)

print()
print("O arquivo abaixo contém a resposta completa do TRF5:")
print(arquivo_html)
