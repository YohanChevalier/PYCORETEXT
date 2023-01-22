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
Module contenant la classe principale de l'application, l'objet Tk
"""

import tkinter as tk
from tkinter import BooleanVar, messagebox
from .api_controller import api_connexion as co, api_url
from .views import login_page as l_pg, homepage as h, result_page
from .widgets import CustomNotebook
from . import exceptions as exc
from pathlib import Path
import sys


class Application(tk.Tk):
    """ Classe principale de l'application"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # chemins d'accès pour l'image et le texte
        # il change selon si nous sommes dans un fichier frozen (exécutable)
        # ou dans la structure normale du projet
        if getattr(sys, 'frozen', False):
            self._c_dir = Path(sys.executable).parent
        else:
            self._c_dir = Path(__file__).parent
        # variables de gestion de la connexion
        self.connexion = None
        self.__connexion_exists = BooleanVar()
        self.__connexion_exists.trace_add("write", self._once_co_up)
        # paramétrage de la fenêtre principale Tk
        self.title("PYCORETEXT")
        self.iconbitmap(default=self._c_dir / "pycoretext.ico")
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        # placer la fenêtre principale au centre de l'écran
        self._app_width = 1200
        self._app_height = 600
        self._screen_width = self.winfo_screenwidth()
        self._screen_height = self.winfo_screenheight()
        self._center_x = int(self._screen_width / 2 - self._app_width / 2)
        self._center_y = int(self._screen_height / 2 - self._app_height / 2)
        self.geometry(
            f'{self._app_width}x{self._app_height}' +
            f'+{self._center_x}+{self._center_y}')
        # création de la login page
        self._login = l_pg.LoginPage(self)
        # on lie l'événement <<Connexion>> généré dans LoginPage à notre app
        self._login.bind('<<Connexion>>', self._on_connexion)
        # fenêtre principale masquée au démarrage
        self.withdraw()
        # initialisation du gestionnaire d'événements
        self.mainloop()

    def _on_connexion(self, *_):
        """
        Vérification de la connexion avec les identifiants collectés
        dans la login page.
        """
        self.connexion = co.Connexion(
            env=self._login.var["environment"].get(),
            key_user=self._login.var["key"].get()
            )
        test_result = self.connexion.test_connexion()
        if isinstance(test_result, bool):
            # si le test est correct alors c'est parti !
            self.__connexion_exists.set(True)
        else:
            # On envoie le message de l'exception à la page login
            self._login.var["error_message"].set(
                f"Erreur de connexion : {test_result}")
            # On retire l'objet connexion s'il n'est pas valide
            self.connexion = None
            # Suppression de la fenêtre d'attente
            self._login.waiting_dialog.destroy()

    def _once_co_up(self, *args, **kwargs):
        """
        Si la variable self.__connexion_exists est modifiée
        alors on initialise la page principale (homepage)
        """
        # création du notebook d'après la classe personnalisée
        # qui offre des onglets avec croix pour fermer
        self._notebook = CustomNotebook(self)
        self._notebook.grid(sticky=tk.W + tk.E + tk.N + tk.S)
        # ajout de la page d'accueil "homepage" dans le notebook
        # on transmet la connexion pour les requêtes internes
        try:
            self._homepage = h.Homepage(self._notebook, self.connexion)
        except exc.ERRORS as e:
            # envoi du message de l'exception à la page login
            self._login.var["error_message"].set(
                f"Erreur de connexion : {e}")
            # suppression de l'objet connexion s'il n'est pas valide
            self.connexion = None
            # suppression de la fenêtre d'attente
            self._login.waiting_dialog.destroy()
            # suppression du notebook
            del self._notebook

        else:
            self._notebook.add(self._homepage, text="Accueil")
            # on bind la fonction de recherche
            self._homepage.search.bind("<<OnSearch>>", self._on_search)
            # On supprime la page de login lorsque tout est initialisé
            self.deiconify()
            self._login.destroy()
            # Suppression de la fenêtre d'attente
            self._login.waiting_dialog.destroy()

    def _on_search(self, *_):
        """
        Méthode qui récupère les données du formulaire
        """
        # affichage d'une fenêtre d'attente
        self.waiting_dialog = tk.Toplevel(
            self,
        )
        # placement de la fenêtre d'attente au centre de la page login
        waiting_dialog_width = 150
        waiting_dialog_heigth = 20
        diff_x = self._app_width // 2 - waiting_dialog_width // 2
        diff_y = self._app_height // 2 - waiting_dialog_heigth // 2
        waiting_dialog_x = self.winfo_rootx() + diff_x
        waiting_dialog_y = self.winfo_rooty() + diff_y
        self.waiting_dialog.geometry(
            f'{waiting_dialog_width}x{waiting_dialog_heigth}' +
            f'+{waiting_dialog_x}+{waiting_dialog_y}')
        # création du message d'attente
        tk.Label(self.waiting_dialog,
                 text="Recherche en cours...").grid(sticky=("we"))
        # rafraîchir la main loop afin d'afficher la page d'attente
        self.update()
        # appel de la fonction get() de SearchBloc afin de récolter les
        # informations données par l'utilisateur dans le formulaire
        data_from_dict = self._homepage.search.get()
        # vérifier si le formulaire est bien complété
        state = self._check_form_integrity(data_from_dict)
        if not state:
            return
        # création de l'objet URL
        url = self._create_url(data_from_dict)
        # suppression des éventuelles réponses internes stockées dans le dict
        if "internal" in self.connexion.dict_answers:
            del self.connexion.dict_answers["internal"]
        # envoi requête à l'API
        try:
            self.connexion.send_request(url)
        except exc.NoResult as e:
            self.waiting_dialog.destroy()
            messagebox.showinfo(
                title="Aucun résultat",
                message=e.message)
            return
        except ValueError as e:
            self.waiting_dialog.destroy()
            messagebox.showinfo(
                title="Communication API",
                message=e)
            return
        except exc.WrongCriteria as e:
            self.waiting_dialog.destroy()
            messagebox.showinfo(
                title="Critères erronés",
                message=e.message)
            return
        else:   # si aucune exception = création de la page de résultat
            id_list = list(self.connexion.dict_answers.keys())
            last_id = 0
            for id in id_list:
                if int(id) > last_id:
                    last_id = id
            last_answer = self.connexion.dict_answers[last_id]
            self._result_page = result_page.ResultPage(
                                    self._notebook,
                                    last_answer)
            self._notebook.add(self._result_page,
                               text=f"Recherche {last_answer.id_answer}")
            self._notebook.select(self._result_page)
            self.waiting_dialog.destroy()

    def _create_url(self, data_from_dict: dict):
        """
        Fonction qui permet de forger l'url avec les données collectées
        """
        # création d'une liste avec les clés du dict
        keys_list = list(data_from_dict.keys())
        # obtenir la classe Url adéquate en fonction de la liste de clé
        good_url_class = api_url.UrlBase.determine_url_type(keys_list)
        # forger l'URL selon la classe obtenue
        # supprimer du dictionnaire les critères à fournir en argument de l'Url
        if good_url_class.__name__ == "UrlDecision":
            url = good_url_class(data_from_dict.pop("id"))
        elif good_url_class.__name__ == "UrlSearch":
            url = good_url_class(data_from_dict.pop("query"))
        # création d'instance ne nécessitant pas d'argument
        else:
            url = good_url_class()
        print("url object =", url)
        # ajouter les autres critères dans l'URL
        if data_from_dict:
            self._add_criterias_in_url(url, data_from_dict)
        return url

    def _add_criterias_in_url(self, url: api_url.UrlBase, data: dict):
        """
        Ajoute les critères à l'objet URL et vide le dictionnaire
        """
        for key, value in data.items():
            # les valeurs sont séparées par '/' dans la value du dict
            values_list = value.split("/")
            old_key = ""
            # des cas exceptionnels à gérer
            if key == "idT":
                old_key = key
                key = "id"
            elif key == "theme ca":
                old_key = key
                key = "theme"
            elif key == "location ca":
                old_key = key
                key = "location"
            for value in values_list:
                url.set_criteria(key + "=", value)
        # suppression de la clé dans le dictionnaire
        if old_key:
            del data[old_key]
        else:
            del data[key]

    def _check_form_integrity(self, data: dict):
        """
        Génère des boîte de dialogue si le formulaire n'est pas correctement
        complété (ex : formulaire vide)
        """
        state = 1
        if not data:
            messagebox.showwarning(
                title="Formulaire vide",
                message="Aucun champ du formulaire n'est complété !")
            state = 0
        elif "key" in data or "value" in data:
            if "idT" not in data:
                messagebox.showerror(
                    title="Critère 'Métadonnée' manquant",
                    message=("Veuillez sélectionner un élément dans le "
                             "critère 'Métadonnée' (bloc 'Recherche par "
                             "critères')")
                )
                state = 0
        elif "operator" in data and "query" not in data:
            messagebox.showerror(
                title="Mot(s) clé(s) manquant(s)",
                message="Le critère 'operator' ne peut pas être utilisé seul."
            )
            state = 0
        return state
