import requests
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://servicebus2.caixa.gov.br/portaldeloterias/api/loteca/1260"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
}

resposta = requests.get(url, headers=headers, verify=False)
dados = resposta.json()

# Imprime a estrutura original que a Caixa usa
print(json.dumps(dados, indent=4, ensure_ascii=False))