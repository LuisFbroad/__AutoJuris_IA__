import requests
from bs4 import BeautifulSoup


url_base = "https://cp.trf5.jus.br"

headers = {
    "User-Agent": "Mozilla/5.0"
}


cpf = "17391998000103"


limite = int(input("Quantas páginas deseja buscar? "))


for pagina in range(limite):

    url = (
        f"{url_base}/processo/rpvprec/"
        f"filtroRPVPrec/cpfcnpj/porData/"
        f"tiporpv/ativos/vinculados/"
        f"{cpf}//{pagina}"
    )

    print("\nAcessando página:", pagina)
    print(url)


    resposta = requests.get(
        url,
        headers=headers,
        timeout=15
    )


    print("Status:", resposta.status_code)


    soup = BeautifulSoup(
        resposta.text,
        "html.parser"
    )


    processos = soup.find_all(
        "a",
        class_="linkar"
    )


    total = 0


    for processo in processos:

        href = processo.get("href")
        numero = processo.text.strip()


        if href and "/processo/" in href:

            print(numero)
            total += 1


    print("Processos encontrados:", total)