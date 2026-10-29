
import requests
import time
from getpass import getpass

documento = getpass("CPF/CNPJ (entrada oculta): ").strip()
tipo = input("Tipo (CPF/CNPJ): ").strip().upper()
digitos = "".join(c for c in documento if c.isdigit())

esperado = {"CPF": 11, "CNPJ": 14}

if tipo not in esperado or len(digitos) != esperado[tipo]:
    print("Documento ou tipo inválido.")
    raise SystemExit(1)

url = (
    "https://cp.trf5.jus.br/processo/rpvprec/"
    "filtroRPVPrec/cpfcnpj/porData/tiporpv/"
    f"ativos/vinculados/{digitos}//0"
)

inicio = time.perf_counter()

try:
    resposta = requests.get(
        url,
        timeout=(8, 45),
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/131.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,*/*;q=0.8"
            ),
            "Accept-Language": "pt-BR,pt;q=0.9",
        },
    )

    print("HTTP:", resposta.status_code)
    print("Tempo:", round(time.perf_counter() - inicio, 2), "s")
    print("Bytes recebidos:", len(resposta.content))
    print("Tipo:", resposta.headers.get("Content-Type"))

except requests.RequestException as erro:
    print("Erro:", type(erro).__name__)
    print("Tempo:", round(time.perf_counter() - inicio, 2), "s")
    print("Mensagem:", str(erro).split(" for ")[0])
