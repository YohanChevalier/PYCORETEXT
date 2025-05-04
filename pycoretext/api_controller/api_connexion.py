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

import requests
from pycoretext import exceptions as exc
from . import api_answers as ans, api_url
import ratelimit
import backoff
import logging
import random


logger_api = logging.getLogger('api.api_connexion')


class Connexion:
    """
    Etablissement d'une connexion à l'env. de QA ou de PRO Judilibre.
    Elle contient les méthodes de test, de requêtage et retour.
    """
    # Permettra de compter les requêtes envoyées à l'API
    requests_number = 0
    # Compte les requêtes qui ont échoué (peu importe la raison)
    abandoned_requests_number = 0

    # constructeur avec 3 paramètres facultatifs : la clé d'auth.,
    # l'env et le mode
    def __init__(self, key_user: str, env='sandbox', test_mode=False):
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
        # le mode test est-il activé
        self.test_mode = test_mode
        # créer la session HTTP
        self.session = requests.Session()
        self.session.headers = {'accept': 'application/json',
                                'KeyId': key_user}
        # 1/ nombre d'objets Answer créés
        # 2/ idendifiant du dernier objet Answer généré
        # 3/ collection des objets Answer sous forme de dict.
        self.nb_answers, self.current_id_answer, self.dict_answers = 0, 0, {}

    @staticmethod
    def filter_wrong_codes(e):
        """
        Analyse l'exception prise par backoff lors
        de l'exécution de la fonction simple_api_request

        Si HTTPError alors vérification du code :
         - Erreurs serveur (>=500) = répétition (False)
         - Erreurs client spécifiques (429, 416) = répétition (False)
         - Autres erreurs clients = Give up
         Si ratelimit.RateLimitException:
          Ne compte pas la requête puisqu'elle n'est pas arrivée à l'API
        """
        if isinstance(e, requests.exceptions.HTTPError):
            if e.response.status_code >= 500:
                Connexion.requests_number += 1
                return False
            elif e.response.status_code in [429, 416]:
                Connexion.requests_number += 1
                return False
            else:
                return True
        elif isinstance(e, ratelimit.RateLimitException):
            return False
        Connexion.requests_number += 1
        return False

    @staticmethod
    def _backoff_on_backoff(details):
        """
        Log warning in case of backoff
        """
        logger_api.warning("Backing off {wait:0.1f} seconds"
                           "after {tries} tries"
                           " ==> Exception: {exception}".format(**details))

    @staticmethod
    def _backoff_on_giveup(details):
        """
        Log error in case of giveup
        """
        logger_api.error("Give up after {tries} tries"
                         " ==> Exception: {exception}".format(**details))
        Connexion.abandoned_requests_number += 1

    @staticmethod
    def _backoff_on_success(details):
        """
        Log info in case of success
        """
        logger_api.info("Success after {tries} tries"
                        " ==> URL: {args[1]}".format(**details))
        Connexion.requests_number += 1

    @backoff.on_exception(backoff.expo,
                          (requests.exceptions.Timeout,
                           ratelimit.RateLimitException,
                           requests.exceptions.HTTPError),
                          max_tries=5,
                          giveup=filter_wrong_codes,
                          on_success=_backoff_on_success,
                          on_backoff=_backoff_on_backoff,
                          on_giveup=_backoff_on_giveup,
                          logger=None)
    @ratelimit.limits(calls=19, period=1)
    def simple_api_request(self, url: str):
        """
        Envoyer une requête à l'API

        ratelimit: 19 calls par seconde
        backoff:
         Si exception timeout, ratelimit ou HTTPError selon le code
         Alors répétion de la fonction, pas plus de 5 fois
         avant d'abandonner.
         Aucun logger propre à backoff
        """
        response = self.session.get(url, timeout=8)
        # Génération aléatoire d'erreurs dans le mode de test
        if self.test_mode:
            random_test = random.randrange(0, 15)
            if random_test == 0:
                raise requests.exceptions.Timeout('timeout')
            elif random_test == 1:
                raise ratelimit.RateLimitException('oops', 1)
            elif random_test == 2:
                # server unavailable
                response.status_code = 503
            elif random_test == 3:
                # Not found
                response.status_code = 404
            else:
                pass
        # If wrong status a HTTPError is raised
        response.raise_for_status()
        return response

    def test_connexion(self):
        """
        Test simple de connexion:
        retourne True si succès, message d'erreur (str) si échec
        """
        is_request_ok = None
        url = self.endpoint + "/healthcheck"
        try:
            self.simple_api_request(url)
        except exc.ERRORS as e:
            # Le message de l'exception est placé dans la variable de retour
            is_request_ok = e
        else:
            is_request_ok = True
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
                response = self.simple_api_request(full_url)
            # la première requête, si elle est en erreur
            # génère automatiquement une exception.
            except exc.ERRORS as e:
                raise e
            else:
                # tentative de création de l'objet Anwser
                try:
                    self._create_answer(response,
                                        url_object.url_type,
                                        url_object.dict_criterias,
                                        full_url, internal,
                                        url_object.integral)
                except exc.NoResult as e1:
                    raise e1

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
                                              self,
                                              # info pour nouvelle requête
                                              first_url)
                # sinon un simple objet Answer suffit
                else:
                    answer = ans.Answer(dict_from_response,
                                        id_answer,
                                        dict_criterias,
                                        connexion=self)
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
                                              self,
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
            answer = ans.Answer(dict_from_response,
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
