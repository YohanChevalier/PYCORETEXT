import requests

# API KEY disponible sur le compte PISTE
api_key = 'XXXX'
# Authentification avec la Key ID
headers = {"accept": "application/json",
           'KeyId': 'XXXX'}
# Permet de vérifier la disponibilité du service
check_service = "healthcheck"
# Permet d'obtenir le contenu d'une décision grâce à son identifiant Judilibre
decision = "decision?id="
true_reference = "&resolve_references=true"
# Permet de rechercher une décision mais pas d'obtenir son contenu
query = "search?query="
taxonomy = "taxonomy?id="
# END POINT
url_base = "https://sandbox-api.piste.gouv.fr/cassation/judilibre/v1.0/"
url_end_point = "decision?id=635a28bd5add2805a756859d"
url_end_point1 = ("search?query=20-86.857")

url = url_base + url_end_point
response = requests.get(url, headers=headers)
response = response.json()
print(response)