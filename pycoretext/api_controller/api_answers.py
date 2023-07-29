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
from math import ceil
from concurrent.futures import ThreadPoolExecutor
from pycoretext import exceptions as exc
import logging

logger_api = logging.getLogger('api.api_answer')

class Answer:
    """
    Reçoit en argument la réponse Judilibre sous forme de dictionnaire.
    Récupère certaines données (page, batch, total).
    Crée les objets Decision et les ajoute au dictionnaire de décisions.
    """

    def __init__(self, dict_from_response, id_answer, dict_criterias,
                 connexion=None):
        """
        Constructeur de la classe Answer
        """
        # récupération de la réponse à la requête sous forme de dict.
        self.dict_from_response = dict_from_response
        # identifiant de la réponse API
        self.id_answer = id_answer
        # critères de recherches issus de l'objet Url
        self.dict_criterias = dict_criterias
        # Récupération de la connexion
        if connexion:
            self.connexion = connexion
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
                 connexion, first_url):
        """
        Constructeur de la classe AnswerExport
        """
        # récupération des informations de connexion
        # !! important de commencer par cette étape
        self.first_url = first_url
        # appelle le constructeur parent
        super().__init__(dict_from_response, id_answer, dict_criterias,
                         connexion)
        # nombre de décisions contenues dans cet objet Answer
        self.nb_decision = 0
        # identifiant de la dernière décision créée
        self._current_id_decision = 0
        # liste des urls dont les requêtes ont rencontré des erreurs
        self.wrong_urls = []
        # dictionnaire qui contiendra l'ensemble des objets Decision
        self.dict_decisions = {}
        # construction de la liste d'urls
        if 'next_page' in dict_from_response:
            # attribut présent dans les réponses Search
            # J'ai choisi des valeurs identiques mais cela pourrait changer
            default_nb_decisions_in_dict = 50
        else:
            # attribut présent dans les réponses Export
            # par défaut, il y a 50 résutats par page pour Export
            default_nb_decisions_in_dict = 50
        # pour Export et Search, plusieurs batchs ou pages doivent être traités
        # le dict_from_response ne correspond qu'au premier d'entre eux
        # nous pouvons à partir de cette donnée et du nombre de résultats
        # obtenir le nombre d'URLs à traiter
        self.number_of_urls = ceil(
                    self.total_decisions / default_nb_decisions_in_dict)
        # création de la liste des Url à partir du résulat de la 1ere page
        urls_list = self._start_create_urls_list()
        # Liste qui contiendra les mauvaises réponses (429 ou 416)
        self._wrong_response_list = {}
        # Threading = requête pour chaque url et création de Decision
        # Solution trouvée : https://realpython.com/python-concurrency/
        # création de l'objet thread.local
        # self._thread_local = threading.local()
        self._generate_decisions(urls_list)
        # --------------------
        # Vérification des résultats
        # --------------------
        logger_api.debug(f'Nb of URLs : {self.number_of_urls}')
        logger_api.debug('Nb décisions annoncées par API :'
                         + f' {self.total_decisions}')
        logger_api.debug('Nb décisions obtenues par Pycoretext :'
                         + f' {self.nb_decision}')
        logger_api.debug('Nb requêtes erronées :'
                         + f' {len(self._wrong_response_list)}')

    def _start_simple_api_request(self, url):
        """
        Exécuter la fonction de requête à l'API.
        Les exceptions issus des abandons Backoff
        ne déclenchent aucune action car elles apparaîtront
        en résultat nul dans la liste de résultats du
        ThreadPoolExecutor
        """
        try:
            response = self.connexion.simple_api_request(url)
        except exc.ERRORS:
            self.wrong_urls.append(url)
        else:
            return response

    def _generate_decisions(self, urls_list):
        """
        Lance les workers (threads) sur la fonction principale
        """
        # 10 est suffisant
        # tous les workers doivent avoir terminé
        # avant de récupérer les résultats
        with ThreadPoolExecutor(max_workers=10) as executor:
            # mapping sur la fonction de requêtage
            results = executor.map(self._start_simple_api_request,
                                   urls_list)
            executor.shutdown(wait=True)
        # récupération des résultats et traitement de chaque résultat
        for r in results:
            # si le résultat est nul à cause d'une exception, on ne traite pas
            if r:
                try:
                    r = r.json()
                except Exception as e:
                    print(e)
                else:
                    self._decision_creation(r)

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

    def _start_create_urls_list(self):
        """
        Exécute la fonction de création de la liste des URLs
        Selon le type de réponse, l'expression à rechercher pour les
        remplacements varie.
        """
        return self._create_urls_list(self.first_url, self.number_of_urls,
                                      "batch=")

    def _create_urls_list(self, first_url, last_index, str_to_search):
        """
        Crée la list des urls
        """
        urls_list = []
        # compteur pour le contrôle de la boucle
        count = 0
        # tant que nous n'avons pas dépassé le nb de pages maximal
        while count < last_index:
            # ajout de l'url en cours de traitement dans la liste
            urls_list.append(first_url)
            count += 1
            current_index = ''
            # a quel index débute le numéro de page dans l'url ?
            start_index = first_url.find(str_to_search) + len(str_to_search)
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
            first_url = first_url.replace(str_to_search + current_index,
                                          str_to_search + new_index)
        return urls_list


class AnswerSearch(AnswerExport):
    """
    Classe dérivée de AnswerExport qui permettra d'adapter certaines
    méthodes à Search
    """

    def __init__(self, dict_from_response, id_answer, dict_criterias,
                 connexion, first_url):
        """
        Constructeur de la classe
        """
        super().__init__(dict_from_response, id_answer, dict_criterias,
                         connexion, first_url)

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

    def _start_create_urls_list(self):
        """
        Exécute la fonction de création de la liste des URLs
        Selon le type de réponse, l'expression à rechercher pour les
        remplacements varie.
        """
        return self._create_urls_list(self.first_url, self.number_of_urls,
                                      "page=")


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
