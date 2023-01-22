"""
Objectif du test : comment transformer les données récupérées sur l'API en
dataframe Pandas.
"""
# %% MISE EN PLACE

import pandas as pd
import json
import requests
import os

# API KEY disponible sur le compte PISTE
api_key = 'XXXX'
# Authentification avec la Key ID
headers = {"accept": "application/json",
           'KeyId': 'XXXX'}
# END POINT
url_search = ("https://sandbox-api.piste.gouv.fr/cassation/judilibre/v1.0/"
              "search?query=boulangerie&type=arret&publication=b")
url_export = ("https://sandbox-api.piste.gouv.fr/cassation/judilibre/v1.0/"
              "export?type=ordonnance&date_start=2022-10-15&"
              "date_end=2022-10-20&date_type=creation&batch=0")
# On télécharge les fichiers json qui nous serviront de tests
# Mais une seule fois afin de ne pas effectuer des requêtes pour rien
if not os.path.exists("search_dataframe.json"):
    try:
        response_search = requests.get(url_search, headers=headers)
    except Exception as e:
        print(e)
    else:
        response_search = response_search.json()
        with open("dataframe_search.json", "w", encoding="utf-8") as f:
            json.dump(response_search, f, ensure_ascii=False, indent=4)

if not os.path.exists("export_dataframe.json"):
    try:
        response_export = requests.get(url_export, headers=headers)
    except Exception as e:
        print(e)
    else:
        response_export = response_export.json()
        with open("dataframe_export.json", "w", encoding="utf-8") as f:
            json.dump(response_export, f, ensure_ascii=False, indent=4)

# %% CREATION DES DATAFRAME

# On crée le dataframe pour la requête Search
# D'abord on convertit le fichier json en objet Python
with open("dataframe_search.json", "r", encoding="utf-8") as f:
    data_s = json.load(f)

# On passe l'objet python à pandas en ciblant les résultats
df_s = pd.DataFrame(
    data_s["results"],
        )

# On crée le dataframe pour la requête Search
# D'abord on convertit le fichier json en objet Python
with open("dataframe_export.json", "r", encoding="utf-8") as f:
    data_e = json.load(f)

# On passe l'objet python à pandas en ciblant les résultats
df_e = pd.DataFrame(
    data_e["results"],
        )

# %% ANALYSE

print(df_e.info())
text = df_e[0:1]["text"]
print(type(text))
new_text = text.to_string()
print("new_text = ", new_text)

# %%
