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
Module définissant les classes de construction de l'Url de recherche Judilibre
Le but est d'obtenir la partie variable de l'Url pour composer la requête.
La base de l'Url (endpoint) proviendra du module judilibre_connexion
"""

from pycoretext import exceptions as exc


class UrlBase:
    """
    Classe parente des sous-classes UrlSearch, UrlDecision, UrlExport, etc.
    Ces dernières instancient des objets qui sont des Url Judilibre correctes.
    """

    def __init__(self, integral=True):
        "Constructeur de l'objet Url."
        # variable contenant un bouléen qui détermine si oui ou non
        # un objet AnswerExport est nécessaire ou si un objet Answer simple
        # est suffisant. Par défaut = True
        self.integral = integral
        # partie variable de l'url
        self.final_url = ""
        # enregistre le mode de recherche
        self.url_type = "base"
        # compte le nombre de critères utilisés dans la requête
        self.nb_criterias = 0
        # sauvegarde les critères utilisés et leurs valeurs
        self.dict_criterias = {}

    def set_criteria(self, criteria, value):
        """
        Ajoute un critère de recherche à la requête HTML.
        L'agument 'criteria' doit se terminer par '=' si une valeur est donnée.
        L'argument 'value' peut être vide.
        """
        if value:
            if criteria[-1] != "=":
                raise exc.WrongCriteria(
                                criteria,
                                "Sigle '=' manquant à la fin du critère")
        # ajout de "&" si un critère préexiste
        if self.nb_criterias >= 1:
            self.final_url += "&"
        # concaténation de l'url de base, du critère et de la valeur
        self.final_url += criteria + value
        self.nb_criterias += 1
        # ajout du critère et de sa valeur dans le dictionnaire
        if criteria in self.dict_criterias:
            self.dict_criterias[criteria].append(value)
        else:
            self.dict_criterias[criteria] = [value]

    def get_final_url(self):
        "Retourne la partie varialbe finale de l'Url"
        # vérification de l'Url avant de la transmettre
        # un exception sera levée dans check _final_url() si erreur
        self._check_final_url()
        return (self.final_url)

    def _check_final_url(self):
        """
        Fonction utile dans les classes enfants après dérivation
        """
        pass

    @classmethod
    def determine_url_type(cls, data):
        """
        Détermine le type d'URL à créer à partir d'une liste de critères
        Retourne un objet Url.
        """
        if "id" in data:
            return UrlDecision
        if "query" in data or "operator" in data:
            return UrlSearch
        if "idT" in data:
            return UrlTaxonomy
        else:
            return UrlExport


class UrlSearch(UrlBase):
    """
    Permet de forger une requête de type Search. C'est à dire qui contient une
    recherche par mot(s) clé(s) (obligatoire) accompagné(s) ou non d'autres
    critères. Le résultat sera une DecisionShort dans api_answers.
    """
    # commande obligatoire pour Search
    _search_base = "/search?"
    _page_size = 50
    # !! cet objet attend un str. En l'occurence, les mots clés choisis

    def __init__(self, query: str, integral=True):
        """
        Fonction d'initialisation
        """
        super().__init__(integral)
        # type de recherche
        self.url_type = "search"
        # ajout de la base
        self.final_url += self._search_base
        # ajout des critères obligatoires
        self._page = 0
        self._query = query
        # ajout du critère page_size à 50
        self.set_criteria('page_size=', str(self._page_size))
        self.set_criteria("query=", self._query)
        self.set_criteria("page=", str(self._page))

    def _check_final_url(self):
        """
        Spécifique à la méthode Search
        Vérifie qu'aucun critère de la méthode Export n'ait été utilisée.
        """
        for crit in self.dict_criterias:
            if crit in ['date_type=', 'batch_size=', 'batch=']:
                raise exc.WrongCriteria(
                                        crit,
                                        'Critère non accepté pour Search')


class UrlExport(UrlBase):
    """
    Permet de forger une requête de type Export. C'est à dire sans recherche
    par mot clé mais selon au moins un critère.
    Le résulat sera DecisionFull dans api_answers.
    """
    # commande et critères obligatoires pour Export
    _export_base = "/export?"
    _batch = 0
    _batch_size = 50

    def __init__(self, integral=True):
        """
        Fonction d'initialisation
        """
        super().__init__(integral)
        # type de recherche
        self.url_type = "export"
        # ajout de la base
        self.final_url += self._export_base
        # ajout du critère batch indispensable
        self.set_criteria('batch=', str(self._batch))
        # ajout du critère batch_size à 50
        self.set_criteria('batch_size=', str(self._batch_size))

    def _check_final_url(self):
        """
        Spécifique à la méthode Export
        Vérifie qu'un critère de la commande Search n'ait été utilisé
        """
        for crit in self.dict_criterias:
            if crit in ['field=', 'page_size=', 'sort=', 'operator=']:
                raise exc.WrongCriteria(
                                        crit,
                                        'Critère non accepté pour Export')


class UrlDecision(UrlBase):
    """
    Permet de forger une Url de type Decision. Elle n'accepte qu'un identifiant
    Judilibre. Le résultat sera DecisionFull dans api_asnwers.
    """
    # commande obligatoire pour Decision
    _export_base = "/decision?"
    # !! l'identifiant étant indispensable, il est demandé lors de l'init

    def __init__(self, judi_id: str, integral=True):
        """
        Fonction d'initialisation
        """
        super().__init__(integral)
        self._judi_id = judi_id
        # type de recherche
        self.url_type = "decision"
        # ajout de la base
        self.final_url += self._export_base
        # ajout du critère id=
        self.set_criteria("id=", self._judi_id)

    def _check_final_url(self):
        """
        Spécifique à la méthode Decision
        Il ne faut qu'un critère.
        """
        if self.nb_criterias != 1:
            raise exc.WrongCriteria(
                    message="Decision doit avoir 1 seul paramètre")


class UrlTaxonomy(UrlBase):
    """
    Permet de forger une requête de type Taxonomy.Sans paramètre, elle retourne
    l'ensemble des critères possibles. Avec un  critère en paramètre, elle
    retourne les valeurs possibles pour celui-ci.
    """
    # commande obligatoire pour Export
    _export_base = "/taxonomy?"

    def __init__(self, integral=True):
        """
        Fonction d'initialisation
        """
        super().__init__(integral)
        # type de recherche
        self.url_type = "taxonomy"
        # ajout de la base
        self.final_url += self._export_base

    def _check_final_url(self):
        """
        Spécifique à la méthode Taxonomy
        Il faut le critère 'id='
        """
        if 'id=' not in self.dict_criterias:
            raise exc.WrongCriteria(
                        message="Taxonomy doit avoir le param. 'id'")


class UrlHealthCheck(UrlBase):
    """
    Permet de foger une requête de type Healthcheck. Elle n'accepte aucun
    paramètre et retournera l'état du service Judilibre
    """
    # commande obligatoire pour Export
    _export_base = "/healthcheck"

    def __init__(self, integral=True):
        """
        Fonction d'initialisation
        """
        super().__init__(integral)
        # type de recherche
        self.url_type = "healthcheck"
        # ajout de la base
        self.final_url += self._export_base

    def _check_final_url(self):
        """
        Spécifique à la méthode Healthcheck
        Il ne faut aucun critère
        """
        if self.nb_criterias:
            raise exc.WrongCriteria(
                        message="Healthcheck n'accepte pas de paramètre")


class UrlStats(UrlBase):
    """
    Permet de forger une requête de type UrlStats.
    Elle n'attend aucun paramètre.
    Elle retournera des statistiques sur la base Judilibre.
    """
    # commande obligatoire pour Export
    _export_base = "/stats?"

    def __init__(self, integral=True):
        """
        Fonction d'initialisation
        """
        super().__init__(integral)
        # mode de recherche
        self.url_type = "stats"
        # ajout de la base
        self.final_url += self._export_base
