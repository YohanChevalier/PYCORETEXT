import requests
from math import ceil
from concurrent.futures import ThreadPoolExecutor
import threading
from ratelimit import limits, RateLimitException
from backoff import on_exception, expo


class AnswerExport:
    """
    Classe dérivée de Answer qui va traiter la réponse d'une requête réalisée
    selon le type d'Url "export".
    """

    def __init__(self, dict_from_response, id_answer, dict_criterias,
                 headers, first_url, total_decisions):
        "Constructeur de la classe AnswerExport"
        self.total_decisions = total_decisions
        # récupération dés informations de connexion
        # !! important de commencer par cette étape
        self.headers, self.first_url = headers, first_url
        print('1ere URL = ', self.first_url)
        # nombre de décisions contenues dans cet objet Answer
        self.nb_decision = 0
        # identifiant de la dernière décision créée
        self.current_id_decision = 0
        # dictionnaire qui contiendra l'ensemble des objets Decision
        self.dict_decisions = {}
        # Construction de la liste d'urls
        if 'next_page' in dict_from_response:
            # attribut présent dans les réponses Search
            # Par défaut, il y a 10 résutats par page pour Search
            default_nb_decisions_in_dict = 10
        else:
            # attribut présent dans les réponses Export
            # Par défaut, il y a 50 résutats par page pour Export
            default_nb_decisions_in_dict = 50
        # pour Export et Search, plusieurs batch ou page doivent être traités
        # le dict_from_response ne correspond qu'au premier d'entre eux
        # grâce à lui, nous connaisons le nb de résulats et nous pouvons alors
        # calculer l'index du dernier batch ou page
        last_index = ceil(self.total_decisions / default_nb_decisions_in_dict)
        print('last index = ', last_index)
        # création de la liste des Url à partir du résulat de la 1ere page
        urls_list = self._create_url_list(self.first_url, last_index)
        print('length url list = ', len(urls_list))
        # création de l'objet thread.local
        self._thread_local = threading.local()
        # Compte le nombre de requêtes
        self._nb_request = 0
        # Liste qui contiendra les mauvaises réponses (429 ou 416)
        self._wrong_response_list = []
        # Threading = requête pour chaque url et création de Decision
        # Solution trouvée : https://realpython.com/python-concurrency/
        self._generate_decisions(urls_list)
        # --------------------
        # Vérification console du résultat
        # --------------------
        # On vérifie le nombre de décisions créées au final
        print('nb_decision = ', self.nb_decision)
        # ainsi que le nombre de mauvaises réponses obtenues
        print('nb 429 = ', self._wrong_response_list.count(429))
        print('nb 416 = ', self._wrong_response_list.count(416))

    def _get_session(self):
        """
        Crée une session requests. on réutilise alors la même TCP connexion
        et on gagne en performance.
        """
        if not hasattr(self._thread_local, "session"):
            self._thread_local.session = requests.Session()
        return self._thread_local.session

#     # Utilisation des modules ratelimit et backoff pour gérer le throttle
#     # 10 requête par seconde et possibilité de retenter 20 fois.
#     @on_exception(expo, RateLimitException, max_tries=20)
#     @limits(calls=10, period=1)
#     def _send_simple_request(self, url):
#         # récupération de la session requests
#         session = self._get_session()
#         # requête elle-même
#         with session.get(url, headers=self.headers) as response:
#             # si le statut est autre que 200 alors on complète la liste
#             # et on lève une exception pour @on_exception decorator
#             if response.status_code != 200:
#                 self._wrong_response_list.append(response.status_code)
#                 raise Exception(
#                     'API response: {}'.format(response.status_code)
#                                )
#             # On incrémente le nb de requêtes
#             self._nb_request += 1
#             # Print utile pour la vérification
#             print(self._nb_request, ' - ', response.status_code, ' - ',
#                   url)
#             # Conversion de la réponse en dict
#             dict = response.json()
#             # Pour chaque élément dans le dictionnaire de la réponse
#             for item in dict['results']:
#                 # On définit l'identifiant du nouvel objet Decision
#                 self.current_id_decision += 1
#                 new_id = self.current_id_decision
#                 # On crée l'objet Décision et on l'ajoute au dico des décisions
#                 self.dict_decisions[new_id] = item["decision_date"]
#                 # On met à jour le nombre de décision
#                 self.nb_decision += 1

#     def _generate_decisions(self, urls_list):
#         "Permet de lancer les workers (threads) sur la fonction principale"
#         # 10 est suffisant
#         with ThreadPoolExecutor(max_workers=10) as executor:
#             executor.map(self.send_simple_request, urls_list)

    # Utilisation des modules ratelimit et backoff pour gérer le throttle
    # 10 requête par seconde et possibilité de retenter 20 fois.
    @on_exception(expo, RateLimitException, max_tries=20)
    @limits(calls=10, period=1)
    def _send_simple_request(self, url):
        # récupération de la session requests
        session = self._get_session()
        # requête elle-même
        with session.get(url, headers=self.headers) as response:
            # si le statut est autre que 200 alors on complète la liste
            # et on lève une exception pour @on_exception decorator
            if response.status_code != 200:
                self._wrong_response_list.append(response.status_code)
                raise Exception(
                    'API response: {}'.format(response.status_code)
                               )
            else:
                return response.json()

    def create_decision(self, dict_from_response):
            # On incrémente le nb de requêtes
            self._nb_request += 1
            # Print utile pour la vérification
            # print(self._nb_request, ' - ', response.status_code, ' - ',
            #       url)
            # Pour chaque élément dans le dictionnaire de la réponse
            for item in dict_from_response['results']:
                # On définit l'identifiant du nouvel objet Decision
                self.current_id_decision += 1
                new_id = self.current_id_decision
                # On crée l'objet Décision et on l'ajoute au dico des décisions
                self.dict_decisions[new_id] = item["decision_date"]
                # On met à jour le nombre de décision
                self.nb_decision += 1
                print(item["decision_date"])

    def _generate_decisions(self, urls_list):
        "Permet de lancer les workers (threads) sur la fonction principale"
        # 10 est suffisant
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(self.send_simple_request, urls_list)
            executor.shutdown(wait=True)
            print("results :")
        for r in results:
            self.create_decision(r)

    def _create_url_list(self, first_url, last_index):
        "Crée la list des urls"
        # Variable qui contiendra la liste des urls
        urls_list = []
        # Compteur pour le contrôle de la boucle
        count = 0
        # Tant que nous n'avons pas dépassé le nb de pages maximal
        while count <= last_index:
            # Ajout de l'url en cours de traitement dans la liste
            urls_list.append(first_url)
            current_index = ''
            # A quel index débute le numéro de page dans l'url
            start_index = first_url.find("batch=") + len('batch=')
            # boucle qui permet de récupérer les chiffres qui composent le
            # numéro de page
            while first_url[start_index].isdigit():
                current_index += first_url[start_index]
                start_index += 1
                # !! on ne poursuit pas si la fin de l'url est atteinte
                if start_index < len(first_url):
                    continue
                else:
                    break
            # On incrémente le numéro de 1
            new_index = str(int(current_index) + 1)
            # Enfin, on remplace le numéro
            first_url = first_url.replace("batch=" + current_index,
                                          "batch=" + new_index)
            count += 1
        return urls_list


if __name__ == "__main__":
    # API KEY disponible sur le compte PISTE
    api_key = 'XXXX'
    # Authentification avec la Key ID
    headers = {"accept": "application/json",
               'KeyId': 'XXXX'}
    # Permet de vérifier la disponibilité du service
    check_service = "healthcheck"
    # Permet d'obtenir le contenu d'une décision grâce à son identifiant
    # Judilibre
    decision = "decision?id="
    true_reference = "&resolve_references=true"
    # Permet de rechercher une décision mais pas d'obtenir son contenu
    query = "search?query="
    taxonomy = "taxonomy?id="
    # END POINT
    url_base = "https://sandbox-api.piste.gouv.fr/cassation/judilibre/v1.0/"
    url_end_point = ("export?batch=0&type=arret&date_start=2000-10-15&"
                     "date_end=2022-10-20&date_type=creation")
    dict_criteria = {"test_key": "test_value"}
    first_url = url_base + url_end_point
    response = requests.get(first_url, headers=headers)
    response = response.json()
    an = AnswerExport(response, "1", dict_criteria, headers, first_url,
                      response["total"])
    # for key, value in an.dict_decisions.items():
    #     print(key, " == ", value)