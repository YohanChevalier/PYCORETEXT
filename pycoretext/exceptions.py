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
Module qui rassemble les exceptions gérées dans le projet pycoretext
"""

import requests
import ratelimit

# variable utilisée dans les différents modules du projet
# liste les exceptions à gérer lors d'une requête API
ERRORS = (
    requests.HTTPError,
    requests.exceptions.Timeout,
    ratelimit.RateLimitException,
    requests.ConnectionError,
    AttributeError,
    ValueError,
    requests.exceptions.RequestException)


class WrongCriteria(Exception):
    """
    Instancie une exception pour gérer les problèmes internes de construction
    des critères
    """
    def __init__(self, criteria='', message='oops, le critère est erroné'):
        self.criteria = criteria
        self.message = message
        super().__init__(self.message)


class NoResult(Exception):
    """
    Une URL de type Export ou Search renvoit aucun résultat
    """
    def __init__(self,
                 message="Aucun résultat trouvé."):
        self.message = message
        super().__init__(self.message)
