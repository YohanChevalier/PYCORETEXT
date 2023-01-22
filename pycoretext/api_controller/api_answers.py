# Copyright 2022, Yohan Chevalier
# This file is part of PYCORETEXT.

# PYCORETEXT is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

# PYCORETEXT is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with PYCORETEXT. If not, see <https://www.gnu.org/licenses/>.

"""
Les classes de ce modules permettent de stocker et structurer les réponses
obtenues par une requête dans l'API
"""
import requests
from math import ceil
from concurrent.futures import ThreadPoolExecutor
import threading
from ratelimit import limits, RateLimitException
from backoff import on_exception, expo


class Answer:
    """
    Reçoit en argument la réponse Judilibre sous forme de dictionnaire.
    Récupère certaines données (page, batch, total).
    Crée les objets Decision et les ajoute au dictionnaire de décisions.
    """

    def __init__(self, dict_from_response, id_answer, dict_criterias):
        """
        Constructeur de la classe Answer
        """
        # récupération de la réponse à la requête sous forme de dict.
        self.dict_from_response = dict_from_response
        # identifiant de la réponse API
        self.id_answer = id_answer
        # critères de recherches issus de l'objet Url
        self.dict_criterias = dict_criterias
        # nombre total de décisions retournées ("total" dans le dict)
        # Si cette clé n'existe pas alors None
        self.total_decisions = self.dict_from_response.get("total", None)

    def feed_dict_decisions(self):
        """
        Crée et liste les objets Decision
        """
        pass


class AnswerExport(Answer):
    """
    Classe dérivée de Answer qui va traiter la réponse d'une requête réalisée
    selon le type d'Url "export".
    """

    def __init__(self, dict_from_response, id_answer, dict_criterias,
                 headers, first_url):
        """
        Constructeur de la classe AnswerExport
        """
        # récupération des informations de connexion
        # !! important de commencer par cette étape
        self.headers, self.first_url = headers, first_url
        print('1ere URL = ', self.first_url)
        # appelle le constructeur parent
        super().__init__(dict_from_response, id_answer, dict_criterias)
        # nombre de décisions contenues dans cet objet Answer
        self.nb_decision = 0
        # identifiant de la dernière décision créée
        self._current_id_decision = 0
        # dictionnaire qui contiendra l'ensemble des objets Decision
        self.dict_decisions = {}
        print('total decisions = ', self.total_decisions)
        # construction de la liste d'urls
        if 'next_page' in dict_from_response:
            # attribut présent dans les réponses Search
            # par défaut, il y a 10 résutats par page pour Search
            default_nb_decisions_in_dict = 10
        else:
            # attribut présent dans les réponses Export
            # par défaut, il y a 50 résutats par page pour Export
            default_nb_decisions_in_dict = 50
        # pour Export et Search, plusieurs batchs ou pages doivent être traités
        # le dict_from_response ne correspond qu'au premier d'entre eux
        # grâce à lui, nous connaissons le nb de résulats et nous pouvons alors
        # calculer l'index du dernier batch ou page
        last_index = ceil(self.total_decisions / default_nb_decisions_in_dict)
        print('last index = ', last_index)
        # création de la liste des Url à partir du résulat de la 1ere page
        urls_list = self._create_urls_list(self.first_url, last_index)
        print('length url list = ', len(urls_list))
        # Compte le nombre de requêtes
        self._nb_request = 0
        # Liste qui contiendra les mauvaises réponses (429 ou 416)
        self._wrong_response_list = {}
        # Threading = requête pour chaque url et création de Decision
        # Solution trouvée : https://realpython.com/python-concurrency/
        # création de l'objet thread.local
        self._thread_local = threading.local()
        self._generate_decisions(urls_list)
        # --------------------
        # Vérification console du résultat
        # --------------------
        # On vérifie le nombre de décisions créées au final
        print('nb_decision = ', self.nb_decision)
        # ainsi que le nombre de mauvaises réponses obtenues
        if self._wrong_response_list:
            for code, nb in self._wrong_response_list.items():
                print(code, " = ", nb)

    def _get_session(self):
        """
        Crée une session requests. on réutilise alors la même TCP connexion
        et on gagne en performance.
        """
        if not hasattr(self._thread_local, "session"):
            self._thread_local.session = requests.Session()
        return self._thread_local.session

    def _generate_decisions(self, urls_list):
        """
        Lance les workers (threads) sur la fonction principale
        """
        # 10 est suffisant
        # tous les workers doivent avoir terminé
        # avant de récupérer les résultats
        with ThreadPoolExecutor(max_workers=10) as executor:
            # mapping sur la fonction de requêtage
            results = executor.map(self._send_simple_request, urls_list[:-1])
            executor.shutdown(wait=True)
        # récupération des résultats et traitement de chaque résultat
        for r in results:
            self._decision_creation(r)

    # ratelimit pour gérer le throttle
    # => 10 requêtes par seconde et possibilité de retenter 20 fois.
    # backoff  pour relancer la fonction en cas d'exception
    @on_exception(expo, RateLimitException, max_tries=20)
    @limits(calls=10, period=1)
    def _send_simple_request(self, url):
        """
        Effectue une requête avec l'url donnée
        Retourne un objet dict
        """
        # récupération de la session requests
        session = self._get_session()
        # requête elle-même
        with session.get(url, headers=self.headers) as response:
            if response.status_code != 200:
                if response.status_code in self._wrong_response_list:
                    self._wrong_response_list[response.status_code] + 1
                else:
                    self._wrong_response_list[response.status_code] = 1
        # incrémenter le nb de requêtes
        self._nb_request += 1
        # print utile pour la vérification par terminal
        print(self._nb_request, ' - ', response.status_code, ' - ',
              url)
        return response.json()

    def _decision_creation(self, dict_from_response: dict):
        """
        Transforme la réponse en objet Decision
        """
        for item in dict_from_response['results']:
            # identification de l'identifiant du nouvel objet Decision
            self._current_id_decision += 1
            new_id = self._current_id_decision
            # création de l'objet Décision et ajout au dict des décisions
            self.dict_decisions[new_id] = DecisionFull(item)
            # mise à jour du nb de décisions
            self.nb_decision += 1

    def _create_urls_list(self, first_url, last_index):
        """
        Crée la list des urls
        """
        urls_list = []
        # compteur pour le contrôle de la boucle
        count = 0
        # tant que nous n'avons pas dépassé le nb de pages maximal
        while count <= last_index:
            # ajout de l'url en cours de traitement dans la liste
            urls_list.append(first_url)
            current_index = ''
            # a quel index débute le numéro de page dans l'url ?
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
            # incrément
            new_index = str(int(current_index) + 1)
            # remplacement du numéro
            first_url = first_url.replace("batch=" + current_index,
                                          "batch=" + new_index)
            count += 1
        return urls_list


class AnswerSearch(AnswerExport):
    """
    Classe dérivée de AnswerExport qui permettra d'adapter certaines
    méthodes à Search
    """

    def __init__(self, dict_from_response, id_answer, dict_criterias,
                 headers, first_url):
        """
        Constructeur de la classe
        """
        super().__init__(dict_from_response, id_answer, dict_criterias,
                         headers, first_url)

    def _decision_creation(self, dict_from_response: dict):
        """
        Transforme la réponse en objet Decision
        """
        for item in dict_from_response['results']:
            # définition de l'identifiant du nouvel objet Decision
            self._current_id_decision += 1
            new_id = self._current_id_decision
            # création de l'objet Décision et ajout au dict des décisions
            self.dict_decisions[new_id] = DecisionShort(item)
            self.nb_decision += 1

    def _create_urls_list(self, first_url, last_index):
        """
        Crée la list des urls
        """
        urls_list = []
        # compteur pour le contrôle de la boucle
        count = 0
        # tant que nous n'avons pas dépassé le nb de pages maximal
        while count <= last_index:
            # ajout de l'url en cours de traitement dans la liste
            urls_list.append(first_url)
            current_index = ''
            # a quel index début le numéro de page dans l'url ?
            start_index = first_url.find("page=") + len('page=')
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
            # incrément
            new_index = str(int(current_index) + 1)
            # remplacement du numéro
            first_url = first_url.replace("page=" + current_index,
                                          "page=" + new_index)
            count += 1
        return urls_list


class AnswerDecision(Answer):
    """
    Classe dérivée qui va analyser la réponse d'une requête réalisée selon le
    mode Decision
    """
    def __init__(self, dict_from_response, id_answer, dict_criterias):
        """
        Fonction d'initialisation
        """
        super().__init__(dict_from_response, id_answer, dict_criterias)
        # toujours 1 seule décision car identifiant judilibre unique
        self.nb_decision = 1
        self.decision = DecisionFull(dict_from_response)


class AnswerTaxonomy(Answer):
    """
    Classe dérivée qui va analyser la réponse d'une requête réalisée selon le
    mode Taxonomy
    """

    def __init__(self, dict_from_response, id_answer, dict_criterias):
        """
        Fonction d'initialisation
        """
        super().__init__(dict_from_response, id_answer, dict_criterias)
        # si aucun id donné alors :
        if dict_criterias["id="][0] == "":
            self.list_results = dict_from_response["result"]
        # traitement particulier de la recherche des thèmes (matières)
        elif dict_criterias["id="][0] == "theme":
            if "context_value=" in dict_criterias:
                # ca: listes dans liste à convertir en tableau
                # key = str: value = list(str)
                # 1er élément de chaque liste est la clé
                if dict_criterias["context_value="][0] == "ca":
                    dict_theme_ca = dict()
                    result = dict_from_response["result"]
                    for el1 in result:
                        # variable pour collecter les clés
                        key = None
                        for i, el2 in enumerate(el1):
                            if i == 0:
                                key = el2
                                dict_theme_ca[key] = list()
                            else:
                                dict_theme_ca[key].append(el2)
                    # l'attribut créé est donc un dictionnaire
                    self.dict_results = dict_theme_ca
                else:
                    # si le contexte est "cc"
                    self.list_results = dict_from_response["result"]
            else:
                # si aucun contexte donné
                self.list_results = dict_from_response["result"]
        else:
            # pour toutes les autres recherches taxonomy
            self.context_value = dict_from_response["context_value"]
            self.dict_results = dict_from_response["result"]


class AnswerHealthCheck(Answer):
    """
    Classe dérivée qui va analyser la réponse d'une requête réalisée selon le
    mode HealCheck
    """

    def __init__(self, dict_from_response, id, dict_criterias):
        """
        Fonction d'initialisation
        """
        super().__init__(dict_from_response, id, dict_criterias)
        self.status = self.dict_from_response["status"]


class AnswerStats(Answer):
    """
    Classe dérivée qui va analyser la réponse d'une requête réalisée selon le
    mode "stats"
    """

    def __init__(self, dict_from_response, id, dict_criterias):
        """
        Fonction d'initialisation
        """
        super().__init__(dict_from_response, id, dict_criterias)
        # liste des métadonnées à conserver (toutes):
        self.meta_list = [
            "requestPerDay", "requestPerWeek", "requestPerMonth",
            "oldestDecision", "newestDecision", "indexedTotal",
            "indexedByJurisdiction", "indexedByYear"
                         ]
        # dictionnaire des métas
        self.dict_meta = dict()
        for meta in self.meta_list:
            self.dict_meta[meta] = dict_from_response.get(
                                                meta,
                                                None)


class DecisionShort:
    """
    Classe qui instancie un objet DecisionShort.
    C'est à dire une décision retournée par Search.
    """
    def __init__(self, dict_from_response):
        """
        Constructeur de l'instance.
        """
        # liste des métadonnées à récupérer
        # certaines ont pu être écartées car inutiles pour le projet
        self.short_meta_list = ["chamber", "decision_date", "ecli", "files",
                                "id", "jurisdiction", "number",
                                "numbers", "publication", "solution",
                                "summary", "themes", "type", "location"]
        # dictionnaire des métas
        self.dict_meta = dict()
        for meta in self.short_meta_list:
            self.dict_meta[meta] = dict_from_response.get(
                                                meta,
                                                None)


class DecisionFull(DecisionShort):
    """
    Classe qui instancie un objet DecisionFull.
    C'est à dire une décision retournée par Export.
    Les attributs sont très complets. Une large sélection est faite.
    """

    def __init__(self, dict_from_response):
        """
        Constructeur de l'instance.
        """
        # liste des métadonnées supplémentaires à récupérer pou DecisionFull:
        # certaines ont pu être écartées car inutiles pour le projet
        self.full_meta_list = [
            "bulletin", "contested", "formation", "forward", "legacy", "nac",
            "partial", "portalis", "rapprochements", "to_be_deleted",
            "solution_alt", "source", "timeline", "update_date", "visa", "text"
                         ]
        super().__init__(dict_from_response)
        # dictionnaire des métas
        for meta in self.full_meta_list:
            self.dict_meta[meta] = dict_from_response.get(
                                                meta,
                                                None)
