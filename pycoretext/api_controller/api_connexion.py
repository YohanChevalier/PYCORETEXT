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
Module contenant les outils nécessaires à la mise en place d'une connexion
entre un utilisateur et l'API Judilibre:
Authentification (API key), vérification du service, vérification d'une URL
créée grâce aux classes du module api_url, requête grâce au module
request et génération de l'objet Answer approprié.
"""

from requests import get as r_get
import requests
from pycoretext import exceptions as exc
from . import api_answers as ans, api_url


class Connexion:
    """
    Etablissement d'une connexion à l'env. de QA ou de PRO Judilibre.
    Elle contient les méthodes de test, de requêtage et retour.
    """

    # constructeur avec 2 paramètres facultatifs : la clé d'auth. et l'env.
    def __init__(self, key_user: str, env='sandbox'):
        self.key_user = key_user
        # le endpoint est différent selon l'env. sélectionné en paramètre
        if env == 'production':
            self.endpoint = (
                'https://api.piste.gouv.fr/cassation/judilibre/v1.0'
            )
        elif env == 'sandbox':
            self.endpoint = (
                'https://sandbox-api.piste.gouv.fr/cassation/judilibre/v1.0'
            )
        # le header est nécessaire lors de la requête request.get (r_get)
        self.headers = {'accept': 'application/json',
                        'KeyId': key_user}
        # 1/ nombre d'objets Answer créés
        # 2/ idendifiant du dernier objet Answer généré
        # 3/ collection des objets Answer sous forme de dict.
        self.nb_answers, self.current_id_answer, self.dict_answers = 0, 0, {}

    def test_connexion(self):
        """
        Test simple de connexion:
        retourne True si succès, message d'erreur (str) si échec
        """
        is_request_ok = None
        try:
            response = r_get(self.endpoint + "/healthcheck",
                             headers=self.headers, timeout=5)
            # une réponse correcte est forcément entre 200 et 300
            if 200 <= response.status_code < 300:
                is_request_ok = True
            else:
                raise ValueError(f"Wrong status: {response.status_code}")
        except requests.ReadTimeout:
            is_request_ok = "API timeout, délai de 5 secondes dépassé"
        except exc.ERRORS as e1:
            # Le message de l'exception est placé dans la variable de retour
            is_request_ok = e1
        finally:
            return is_request_ok

    def send_request(self, url_object: api_url.UrlBase, internal=False):
        """
        Attend un objet URL (cf. module api_answers). A partir de l'url de
        celui-ci, une requête est envoyée. Si la réponse est correcte et
        que des résultats existent alors un objet Answer est créé.
        Le paramètre 'internal' permet de savoir si c'est une requête interne,
        c'est à dire nécessaire au fonctionnement de l'appli  ou à  l'inverse,
        une requête utilisateur.
        """
        # on construit l'url complète (endpoint+partie variable de l'Objet URL)
        # la méthode get_final_url peut lever des exceptions car elle appelle
        # la méthode check_final_url : il faut les gérer avec try-except
        try:
            full_url = "".join([self.endpoint, url_object.get_final_url()])
        except exc.WrongCriteria as e:
            raise e
        else:
            # si url est correcte, tentative de connexion
            try:
                response = r_get(full_url, headers=self.headers,
                                 timeout=5)
                # tester le code de retour
                if 200 <= response.status_code < 300:
                    # on ne fait rien, c'est correct
                    pass
                else:
                    raise ValueError(
                        f"Wrong status: {response.status_code}:")
            # transformation de l'exception de timeout en ValueError
            except requests.ReadTimeout as e1:
                raise ValueError(
                    "Api timeout, délai de 5 secondes dépassé") from e1
            except exc.ERRORS as e2:
                raise e2
            else:
                # tentative de création de l'objet Anwser
                try:
                    self._create_answer(response,
                                        url_object.url_type,
                                        url_object.dict_criterias,
                                        full_url, internal,
                                        url_object.integral)
                except exc.NoResult as e3:
                    raise e3

    def _create_answer(
            self, response: requests.Response,
            url_type: str,
            dict_criterias: dict,
            first_url: str,
            internal: bool,
            integral=None):
        """
        L'objet requests.Response obtenu nous permet de créer un objet
        personnalisé de type Answer (et dérivés)
        """
        # conversion en dict de l'objet json requests.Response
        dict_from_response = response.json()
        is_answer_created = 1
        # création de l'objet Answer selon le type de l'url
        if url_type == "export":
            # si aucun résultat trouvé
            if dict_from_response['total'] == 0:
                # le contrôle revient à 0 pour indiquer que rien n'est créé
                is_answer_created = 0
                # une exception est levée
                raise exc.NoResult()
            else:
                id_answer = self._create_id_answer(internal=internal)
                # création de l'objet Answer
                # si l'objet complet est exigé par l'attribut "integral"
                if integral:
                    answer = ans.AnswerExport(dict_from_response,
                                              id_answer,
                                              dict_criterias,
                                              # info pour nouvelle requête
                                              self.headers,
                                              first_url)
                # sinon un simple objet Answer suffit
                else:
                    answer = ans.Answer(dict_from_response,
                                        id_answer,
                                        dict_criterias)
        # même chose pour search
        elif url_type == "search":
            if dict_from_response['total'] == 0:
                is_answer_created = 0
                raise exc.NoResult()
            else:
                id_answer = self._create_id_answer(internal=internal)
                if integral:
                    answer = ans.AnswerSearch(dict_from_response,
                                              id_answer,
                                              dict_criterias,
                                              self.headers,
                                              first_url)
                else:
                    answer = ans.Answer(dict_from_response,
                                        id_answer,
                                        dict_criterias)
        elif url_type == "decision":
            id_answer = self._create_id_answer(internal=internal)
            answer = ans.AnswerDecision(dict_from_response,
                                        id_answer,
                                        dict_criterias)
        elif url_type == "taxonomy":
            id_answer = self._create_id_answer(internal=internal)
            answer = ans.AnswerTaxonomy(dict_from_response,
                                        id_answer,
                                        dict_criterias)
        elif url_type == "healthcheck":
            id_answer = self._create_id_answer(internal=internal)
            answer = ans.AnswerHealthCheck(dict_from_response,
                                           id_answer,
                                           dict_criterias)
        elif url_type == "stats":
            id_answer = self._create_id_answer(internal)
            answer = ans.AnswerStats(dict_from_response,
                                     id_answer,
                                     dict_criterias)
        if is_answer_created:
            # si un objet Answer a été créé, on l'ajoute dans le dict_answers
            # avec son id
            self.dict_answers[id_answer] = answer
            # incrémenter le nombre de réponses obtenues
            if not internal:
                self.nb_answers += 1

    def _create_id_answer(self, internal):
        """
        Crée l'identifiant de la réponse
        """
        # incrémenter l'identifiant de la prochaine Answer
        if not internal:
            self.current_id_answer += 1
            return self.current_id_answer
        else:
            # dans le cas d'une demande interne le même id sera utilisé et donc
            # écrasé à chaque fois
            return "internal"
