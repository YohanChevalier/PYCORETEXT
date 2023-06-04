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
from tkinter import BooleanVar
from tkinter import ttk
from .api_controller import api_connexion as co, api_url
from .views import login_page as l_pg, homepage as h, result_page
from .widgets import CustomNotebook, place_windows, CustomMessageBox
from . import exceptions as exc
from pathlib import Path
import sys
import threading
import datetime
import logging

# Définir le format des messages logging
FORMAT1 = '[%(asctime)s] %(levelname)s // %(name)s // %(message)s'
FORMAT2 = '[%(asctime)s] %(threadName)s // %(levelname)s // %(name)s // %(message)s'
DATE_FORMAT = '%m-%d-%Y %H:%M:%S'

# Définir un logger root pour le suivi des événements
logger_root = logging.getLogger('flux')
logger_root.setLevel(logging.INFO)

# Définir le handler et le formatter du root
fh = logging.StreamHandler()
formatter = logging.Formatter(FORMAT1, datefmt=DATE_FORMAT)
fh.setFormatter(formatter)
logger_root.addHandler(fh)

# Premier enfant du root flux
logger = logging.getLogger('flux.app')

# Définir un logger pour les appels API
logger_api = logging.getLogger('api')
logger_api.setLevel(logging.INFO)

# Définir le handler et le formatter du logger_api
fh = logging.StreamHandler()
formatter = logging.Formatter(FORMAT2, datefmt=DATE_FORMAT)
fh.setFormatter(formatter)
logger_api.addHandler(fh)


class Application(tk.Tk):
    """ Classe principale de l'application"""

    def __init__(self, *args, **kwargs):
        logger.info('START init of the application')
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
        # paramétrage de la fenêtre principale Tk
        self.title("PYCORETEXT")
        self.iconbitmap(default=self._c_dir / "pycoretext.ico")
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        # placer la fenêtre principale au centre de l'écran
        self._width = 1100
        self._height = 550
        place_windows(self, self._width, self._height)
        # création de la login page
        self._login = l_pg.LoginPage(self)
        # on lie l'événement <<Connexion>> généré dans LoginPage à notre app
        self._login.bind('<<Connexion>>', self._on_connexion)
        # fenêtre principale masquée au démarrage
        self.withdraw()
        # initialisation du gestionnaire d'événements
        logger.info('END init of the application')
        self.mainloop()

    def _on_connexion(self, *_):
        """
        1- création d'une fenêtre pop-up avec label et progress bar
        2- instanciation d'un thread dont la cible est _start_login_connexion
        3- fermeture de la pop-up une fois le thread terminé (observateur sur
        variable) """
        # placement de la fenêtre d'attente au centre de la page login
        # affichage d'une fenêtre d'attente
        self.waiting_login_dialog = tk.Toplevel(
            self._login,
        )
        # Désactiver l'utilisation de la croix rouge pour fermer
        self.waiting_login_dialog.protocol("WM_DELETE_WINDOW",
                                           self._close_waiting_dialog)
        self.waiting_login_dialog.grab_set()
        self.waiting_login_dialog.focus_set()
        self.waiting_login_dialog.columnconfigure(0, weight=1)
        self.waiting_login_dialog.resizable(False, False)
        # Positionnement de la fenêtre
        place_windows(self.waiting_login_dialog, 200, 60, self._login)

        # Label d'attente
        waiting_login_label = ttk.Label(
                                self.waiting_login_dialog,
                                text='Mise en place de l\'application...')
        waiting_login_label.grid(column=0, row=0, sticky=tk.W + tk.E, padx=6)

        # Barre de progression
        pbar = ttk.Progressbar(self.waiting_login_dialog, orient='horizontal',
                               length=100, mode='indeterminate')
        pbar.grid(column=0, row=1, sticky=tk.W + tk.E, padx=6)
        pbar.start(5)

        # Variable d'état pour la mise en place de l'application
        self._login_ready = tk.BooleanVar()

        # Définie la function qui prendra en charge les exceptions
        # levées dans le thread
        threading.excepthook = self._custom_hook_login

        # Ouvre un thread et exécute la fonction cible
        login_thread = threading.Thread(target=self._start_main_window_setup)
        login_thread.start()

        # Attend que le thread ait mis en place la fenêtre principale
        self.wait_variable(self._login_ready)

        # Suppression de la fenêtre d'attente
        self.waiting_login_dialog.destroy()

    def _start_main_window_setup(self):
        """
        1- Vérification de la connexion avec les identifiants collectés
        dans la login page
        2- si ok = construction de la homepage et fermeture de la login page
        3- si ko = envoi de l'erreur dans la login page et nettoyage"""
        logger.info('TRY API connection')
        self.connexion = co.Connexion(
            env=self._login.var["environment"].get(),
            key_user=self._login.var["key"].get()
            )
        test_result = self.connexion.test_connexion()
        if isinstance(test_result, bool):
            logger.info('SUCCES API connection')
            # si le test est correct alors c'est parti !
            self.__connexion_exists.set(True)
            self._build_homepage()
        else:
            logger.error(f'FAIL API connection : {test_result}')
            # On envoie le message de l'exception à la page login
            self._login.var["error_message"].set(
                f"Erreur de connexion : {test_result}")
            # On retire l'objet connexion s'il n'est pas valide
            self.connexion = None
            # suppression de la fenêtre d'attente
            self.waiting_login_dialog.destroy()

    def _build_homepage(self):
        """
        Création de la page d'accueil.
        Envoid e l'éventuelle erreur à la login page
        """
        logger.info('START create homepage')
        # création du notebook d'après la classe personnalisée
        # qui offre des onglets avec croix pour fermer
        self._notebook = CustomNotebook(self)
        self._notebook.grid(sticky=tk.W + tk.E + tk.N + tk.S)
        # ajout de la page d'accueil "homepage" dans le notebook
        # on transmet la connexion pour les requêtes internes
        try:
            self._homepage = h.Homepage(self._notebook, self.connexion)
        except exc.ERRORS as e:
            logging.info(f'FAIL create homepage : {e}')
            # envoi du message de l'exception à la page login
            self._login.var["error_message"].set(
                f"Erreur de connexion : {e}")
            # suppression de l'objet connexion s'il n'est pas valide
            self.connexion = None
            # suppression de la fenêtre d'attente
            self.waiting_login_dialog.destroy()
            # suppression du notebook (widget et variable)
            self._notebook.destroy()
            del self._notebook
        else:
            self._notebook.add(self._homepage, text="Accueil")
            # on bind la fonction de recherche
            self._homepage.search.bind("<<OnSearch>>", self._on_search)
            # Signal pour supprimer la progressbar
            self._login_ready.set(True)
            # On supprime la page de login lorsque tout est initialisé
            self.deiconify()
            self._login.destroy()
            logger.info('SUCCESS homepage created')

    def _custom_hook_login(self, args: threading.ExceptHookArgs):
        """
        Fonction pour gérer les exceptions qui ne sont pas déjà gérées
        dans le code exécuté dans le thread
        """
        # envoi du message de l'exception à la page login
        self._login.var["error_message"].set(
                        f"Type erreur = {args.exc_type}"
                        + "\n"
                        f"Valeur = {args.exc_value}"
                        + "\n"
                        + f"identité thread = {args.thread.getName()}")
        self.waiting_login_dialog.destroy()

    def _on_search(self, *_):
        """
        1- création d'une fenêtre pop-up avec label et progress bar
        2- instanciation d'un thread dont la cible est _start_api_request
        3- fermeture de la pop-up une fois le thread terminé (observateur sur
        variable) """
        # placement de la fenêtre d'attente au centre de la page login
        # affichage d'une fenêtre d'attente
        self.waiting_dialog = tk.Toplevel(
            self,
        )
        # Désactiver l'utilisation de la croix rouge pour fermer
        self.waiting_dialog.protocol("WM_DELETE_WINDOW",
                                     self._close_waiting_dialog)
        self.waiting_dialog.focus_set()
        self.waiting_dialog.grab_set()
        self.waiting_dialog.columnconfigure(0, weight=1)
        self.waiting_dialog.resizable(False, False)
        # Placement de la fenêtre
        place_windows(self.waiting_dialog, 200, 60, root=self)

        # Label d'attente
        waiting_label = ttk.Label(self.waiting_dialog,
                                  text='Requêtes Judilibre en cours...')
        waiting_label.grid(column=0, row=0, sticky=tk.W + tk.E, padx=6)

        # Barre de progression
        pbar = ttk.Progressbar(self.waiting_dialog, orient='horizontal',
                               length=200, mode='indeterminate')
        pbar.grid(column=0, row=1, sticky=tk.W + tk.E, padx=6)
        pbar.start(5)

        # Variable d'état pour la recherche
        self._search_done = tk.BooleanVar()

        # Définie la function qui prendra en charge les exceptions
        # levées dans le thread
        threading.excepthook = self._custom_hook_search

        # Ouvre un thread et exécute la fonction cible
        main_thread = threading.Thread(target=self._start_api_request)
        main_thread.start()

        # Attend que le thread ait modifié l'état de la recherche
        self.wait_variable(self._search_done)

        # Suppression de la fenêtre d'attente
        self.waiting_dialog.destroy()

    def _start_api_request(self):
        """
        Méthode qui récupère les données du formulaire
        """
        logger.info('TRY user API request')
        # appel de la fonction get() de SearchBloc afin de récolter les
        # informations données par l'utilisateur dans le formulaire
        data_from_dict = self._homepage.search.get()
        # vérifier si le formulaire est bien complété
        # Si problème alors :
        # -fin de la recherche
        # -générer les erreurs si nécessaire
        result_integrity = self._check_form_integrity(data_from_dict)
        if not result_integrity[0]:
            self._search_done.set(False)
            CustomMessageBox(
                result_integrity[1], result_integrity[2], "error")
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
            logger.info('NO RESULT user API request')
            self.waiting_dialog.destroy()
            CustomMessageBox(
                "Aucun résultat",
                e.message,
                "error")
            return
        except exc.ERRORS as e:
            logger.error(f'FAIL user API request : {e}')
            self.waiting_dialog.destroy()
            CustomMessageBox(
                "Communication API",
                e,
                "error")
            return
        except exc.WrongCriteria as e:
            logger.error(f'FAIL user API request : {e}')
            self.waiting_dialog.destroy()
            CustomMessageBox(
                "Critères erronés",
                e.message,
                "error")
            return
        else:   # si aucune exception = création de la page de résultat
            logger.info('SUCCESS user request to API')
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
            # mise à jour de la variable qui indique
            # la fin du traitement dans le thread
            self._search_done.set(True)

    def _custom_hook_search(self, args: threading.ExceptHookArgs):
        """
        Fonction pour gérer les exceptions qui ne sont pas déjà gérées
        dans le code exécuté dans le thread
        """
        CustomMessageBox(
            "Erreur technique observé dans un thread",
            (f"Type erreur = {args.exc_type}"
             + "\n"
             f"Valeur = {args.exc_value}"
             + "\n"
             + f"identité thread = {args.thread.getName()}"),
            "error")
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
        Vérifie l'intégrité du formulaire.
        Retourne un tuple composé du state, d'un titre et d'un message
        Si state == 0 alors erreur
        Le titre et le message serviront pour l'affichage d'une messagebox
        """
        state = 1
        title = ""
        message = ""
        if not data:
            title = "Formulaire vide"
            message = "Aucun champ du formulaire n'est complété !"
            state = 0
        elif "key" in data or "value" in data or "context_value" in data:
            if "idT" not in data:
                title = "Critère 'Métadonnée' manquant"
                message = ("Veuillez sélectionner un élément dans le "
                           + "critère 'Métadonnée'")
                state = 0
        elif "operator" in data and "query" not in data:
            title = "Mot(s) clé(s) manquant(s)"
            message = "Le critère 'operator' ne peut pas être utilisé seul."
            state = 0
        elif "location ca" in data or "theme ca" in data:
            juris = data.get("jurisdiction", None)
            if juris is None or juris == "cc":
                title = "Conflit de juridictions"
                message = ("Certains critères ne sont pas compatibles "
                           + "avec la juridiction choisie." + '\n'
                           + "Rappel, la juridiction par défaut est"
                           + "'cc'.")
                state = 0
        # vérification des dates si présentes dans data
        date_to_check = ['date_start', 'date_end']
        for date in date_to_check:
            if date in data:
                if self._date_checker(data[date]) is False:
                    title = "Format de date incorrect"
                    message = ("Soit '2023', soit '2023-01'" +
                               ", soit '2023-01-01'.")
                    state = 0
        return (state, title, message)

    def _close_waiting_dialog(self):
        """
        Action attendue lors du clic sur la croix rouge"""
        pass

    def _on_closing(self):
        """
        Action réalisée lors du clic sur la croix en haut à droite de l'app"""
        CustomMessageBox("Quitter",
                         "Voulez-vous fermer l'application ?",
                         "question")

    def _date_checker(self, date: str):
        check_state = False
        # vérification par format
        for format in ['%Y-%m-%d', '%Y-%m', '%Y']:
            try:
                datetime.datetime.strptime(date, format)
            except ValueError:
                pass
            else:
                check_state = True
        # vérification par nombre de chiffres pour chaque segment
        date_list = date.split("-")
        for i, date in enumerate(date_list):
            if i == 0:
                if len(date) < 4:
                    check_state = False
            elif len(date) < 2:
                check_state = False
        return check_state
