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
Module qui contient les classes de construction pour la homepage.
Une classe générale accompagnée de 3 sous-classes :
3 Frames = "Informations de connexion", "Statistiques Judilibre", "Recherche"
"""

import threading
import tkinter as tk
from tkinter import ttk
from datetime import date as d, timedelta as td
from pycoretext import exceptions as exc, widgets as w
from pycoretext.api_controller import api_url
from pycoretext.widgets import place_windows, CustomMessageBox
from . import form
import logging

logger = logging.getLogger('flux.homepage')


class Homepage(ttk.Frame):
    """
    Entité principale de la homepage, héritée du widget Frame
    """

    def __init__(self, parent, connexion, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.connexion = connexion
        # paramétrage de la fenêtre homepage
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        try:
            logger.info('TRY create SearchBloc part')
            self.search = form.SearchBloc(self, connexion)
            self.search.grid(column=0, row=0, sticky=tk.W + tk.E,
                             padx=10, pady=10)
            self.search.columnconfigure(0, weight=1)
            self.search.columnconfigure(1, weight=1)
        except exc.ERRORS as e:
            logger.error('FAIL create SearchBloc part')
            raise e
        else:
            self.info_button = ttk.Button(self,
                                          text="Informations et statistiques",
                                          command=self._on_click_info)
            self.info_button.grid(column=0, row=1, sticky=tk.W + tk.E,
                                  padx=10)
            # Création des compteurs de requêtes
            self.count_frame = ttk.Frame(self)
            self.count_frame.grid(column=0, row=2, sticky=tk.E,
                                  padx=10)
            self.requests_number = ttk.Label(self.count_frame,
                                             text="Requêtes API correctes : 0",
                                             foreground="green4")
            self.requests_number.grid(column=0, row=0, sticky=tk.E)
            self.abandoned_requests_number = ttk.Label(
                                        self.count_frame,
                                        text=" Requêtes API erronées : 0",
                                        foreground="red")
            self.abandoned_requests_number.grid(column=1, row=0, sticky=tk.E,
                                                padx=10)
            logger.info('SUCCESS create SearchBloc part')

    def _start_display_info(self):
        """
        Affiche la fenêtre de niveau supérieur
        pour les infos de connexion et les stats"""
        logger.info('TRY display InfoPopup')
        try:
            self.info_window = InfoPopup(self, self.connexion)
        except exc.ERRORS as e:
            logger.error('FAIL display InfoPopup')
            self._var_display_info.set(False)
            CustomMessageBox(
                "Impossible d'afficher les informations",
                e,
                type='error',
                root=self.nametowidget("."))
            # Génère un événement pour que l'app actualise
            # le compte des requêtes
            self.event_generate(('<<info_request>>'))
        else:
            self._var_display_info.set(True)
            logger.info('SUCCESS display InfoPopup')
            # Génère un événement pour que l'app actualise
            # le compte des requêtes
            self.event_generate(('<<info_request>>'))

    def _on_click_info(self, *_):
        """
        1- création d'une fenêtre pop-up avec label et progress bar
        2- instanciation d'un thread dont la cible est _display_info
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
        self.waiting_dialog.grab_set()
        self.waiting_dialog.columnconfigure(0, weight=1)
        self.waiting_dialog.resizable(False, False)
        # placement de la fenêtre
        place_windows(self.waiting_dialog, 200, 60,
                      root=self.waiting_dialog.nametowidget("."))
        # Label d'attente
        waiting_label = ttk.Label(self.waiting_dialog,
                                  text='Récupération des informations...')
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
        threading.excepthook = self._custom_hook_display

        # Ouvre un thread et exécute la fonction cible
        main_thread = threading.Thread(target=self._start_display_info)
        main_thread.start()

        # Variable d'attente
        self._var_display_info = tk.BooleanVar()

        # Attend que le thread ait modifié l'état de la recherche
        self.wait_variable(self._var_display_info)

        # Suppression de la fenêtre d'attente
        self.waiting_dialog.destroy()

        # Affichage de la fenêtre d'info
        if self._var_display_info.get():
            self.info_window.deiconify()

    def _custom_hook_display(self, args: threading.ExceptHookArgs):
        """
        Fonction pour gérer les exceptions qui ne sont pas déjà gérées
        dans le code exécuté dans le thread
        """
        CustomMessageBox(
            "Erreur technique observé dans un thread",
            (f"Type erreur = {args.exc_type}"
             + "\n"
             + f"Détail = {args.exc_value}"
             + "\n"
             + f"identité thread = {args.thread.getName()}"),
            "error")
        self.waiting_dialog.destroy()

    def _close_waiting_dialog(self):
        """
        Action attendue lors du clic sur la croix rouge"""
        pass


class InfoPopup(tk.Toplevel):
    """
    Génère une fenêtre de niveau supérieur
    Pour l'affichage des informations de connexion
    et des informations statistiques"""

    def __init__(self, parent, connexion, *args, **kwargs):
        """
        Fonction d'initialisation"""
        # Héritage de l'initialisateur parent
        super().__init__(parent, *args, **kwargs)
        # on masque la fenêtre toplevel
        self.withdraw()
        # Configuration
        self.title("Informations et statistiques")
        self.resizable(False, False)
        # Placement de la fenêtre
        self._width = 250
        self._height = 600
        place_windows(self, self._width, self._height,
                      root=self.nametowidget('.'))

        # création du bloc pour les parties informatives
        main_frame = tk.Frame(self)
        main_frame.grid(column=0, row=0, sticky=tk.W + tk.E + tk.N + tk.S)
        main_frame.columnconfigure(0, weight=1)
        # création du bloc d'infos
        try:
            logger.info('TRY create InfosBloc in InfoPopup')
            service_state = InfosBlocData(connexion)._get_data()
        except exc.ERRORS as e:
            logger.error('FAIL create InfosBloc in InfoPopup')
            raise e
        else:
            infos = InfosBloc(
                main_frame, "Infos", connexion.endpoint,
                connexion.key_user, service_state)
            infos.grid(
                column=0, row=0, sticky=tk.W + tk.E,
                pady=(0, 10), padx=8)
            logger.info('SUCCESS create InfosBloc in InfoPopup')
            # création du bloc des statistiques judilibre
            try:
                logger.info('TRY create StatsBloc in InfoPopup')
                stats = StatsBloc(
                    main_frame, "Statistiques Judilibre",
                    StatsBlocData(connexion)._get_data())
                stats.grid(
                    column=0, row=1, sticky=tk.W + tk.E, padx=8)
            except exc.ERRORS as e1:
                logger.error('FAIL create StatsBloc in InfoPopup')
                raise e1
            else:
                logger.info('SUCCESS create StatsBloc in InfoPopup')


class InfosBloc(tk.LabelFrame):
    """
    un cadre contenant des Labels (environnement, clé, état du service)
    """

    def __init__(self, master, text, env, key, healthcheck, *args, **kwargs):
        """
        fonction d'initialisation
        """
        super().__init__(master=master, text=text, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        #  définition de la valeur d'environnement
        if "sandbox" in env:
            env = "sandbox"
        else:
            env = "production"
        # liste des labels à utiliser pour le widget double_labels
        self._labels = [
            ("Environnement", tk.StringVar(self, env)),
            ("Clé d'authentification", tk.StringVar(
                                       self, self._hide_key(key))),
            ("État du service", tk.StringVar(self, healthcheck)),
        ]
        # création des double_labels
        self._create_double_labels(self._labels)

    def _create_double_labels(self, labels):
        """
        crée les widgets à partir d'une liste de tuple (label, var)
        """
        for label in labels:
            w.DoubleLabel(self, label[0], label[1].get())

    def _hide_key(self, key: str):
        """
        Permet de cacher une grande partie des caractères de la clé
        """
        new_key = key[:2] + "*" * 10 + key[-3:-1]
        return new_key


class InfosBlocData:
    """
    utilise la connexion et récupére les infos internes pour Infos bloc
    """
    def __init__(self, connexion):
        """
        fonction d'initialisation
        """
        self._connexion = connexion
        # envoi de la requête
        try:
            self._connexion.send_request(api_url.UrlHealthCheck(),
                                         internal=True)
        except exc.ERRORS as e:
            raise e
        else:
            self._get_data()

    def _get_data(self):
        """
        Récupère les informations adéquates dans la réponse
        """
        return self._connexion.dict_answers["internal"].status


class StatsBloc(tk.LabelFrame):
    """
    Un cadre contenant des Labels de stats
    """
    def __init__(self, master, text: str, data: list, *args, **kwargs):
        """
        fonction d'initialisation
        """
        super().__init__(master=master, text=text, *args, **kwargs)
        # configuration des colonnes
        self.columnconfigure(0, weight=1)
        # liste des labels à utiliser pour le widget double_labels
        self._data = data
        # liste des labels d'entête pour les sous-frames
        titles_frames = ["Général", "Cour de cassation", "Cours d'appel",
                         "Tribunaux judiciaires", "Tribunaux de commerce"]
        # liste des LabelFrame widget
        labels_list = list()
        # création des sous-frames et des labels à l'intérieur
        for i in range(5):
            labels_list.append(ttk.LabelFrame(
                               self, text=titles_frames[i]))
            labels_list[i].grid(row=i, sticky=tk.W + tk.E,
                                padx=5, pady=5)
            self._create_double_labels(labels_list[i],
                                       self._data[i])

    def _create_double_labels(self, parent, labels):
        """
        Crée les widgets à partir d'une liste de tuple (label, var)
        """
        for label in labels:
            w.DoubleLabel(parent, label[0], label[1])


class StatsBlocData:
    """
    Utilise la connexion et récupére les infos internes pour stats bloc
    """
    def __init__(self, connexion):
        """
        fonction d'initialisation
        """
        self.connexion = connexion
        # variables des listes
        self._dict_lists = {
            "all": [],
            "cc": [],
            "ca": [],
            "tj": [],
            "tcom": []
        }
        # compléter les listes
        self._build_lists()

    def _build_lists(self):
        """
        Complète les listes _all, _cc, _ca et _tj puis les retourne
        """
        # Information de date utile pour les futures requêtes
        today = d.today()
        diff1 = td(days=1)
        yesterday = today - diff1
        month = str(today.month)
        first_day_month = today.replace(day=1)
        last_day_of_prev_month = today.replace(day=1) - td(days=1)
        start_day_of_prev_month = today.replace(day=1) - td(
                                        days=last_day_of_prev_month.day)
        previous_month = last_day_of_prev_month.month
        # 1/ collecter les infos générales
        try:
            self.connexion.send_request(api_url.UrlStats(), internal=True)
        except exc.ERRORS as e:
            raise e
        else:
            dict_answer = self.connexion.dict_answers["internal"]
            results = dict_answer.dict_from_response["results"]
            self._dict_lists["all"].append(
                            ("Nb total des textes",
                             "{:,}".format(results["total_decisions"])))
            self._dict_lists["all"].append(
                            ("Date créa. la plus récente",
                             results["max_decision_date"]))
        # 2/ collecte de statistiques par juridiction
        # 2.1/ nb de textes par juridiction
            for juris in ["cc", "ca", "tj", "tcom"]:
                try:
                    url = api_url.UrlStats()
                    url.set_criteria("jurisdiction=", juris)
                    self.connexion.send_request(url, internal=True)
                except exc.ERRORS as e:
                    raise e
                else:
                    dict_answer = self.connexion.dict_answers["internal"]
                    results = dict_answer.dict_from_response["results"]
                    self._dict_lists[juris].append(
                                ("Nb textes", "{:,}".format(
                                    results["total_decisions"])))
            # 2.2/ Requêtes sur des périodes spécifiques
            # (interne) constantes pour les requêtes :
            # requêtes pour chaque organisme
            for orga in ["cc", "ca", "tj", "tcom"]:
                self._date_request(
                    "Créés hier",
                    yesterday,
                    yesterday,
                    orga
                )
            for orga in ["cc", "ca", "tj", "tcom"]:
                self._date_request(
                    f"Créés mois en cours ({str(month)})",
                    first_day_month,
                    today, orga
                )
            for orga in ["cc", "ca", "tj", "tcom"]:
                self._date_request(
                    f"Créés mois passé ({str(previous_month)})",
                    start_day_of_prev_month,
                    last_day_of_prev_month, orga
                )

    def _date_request(self, label, date_start, date_end,
                      jurisdiction):
        # transformation en string
        date_start, date_end = str(date_start), str(date_end)
        # création de l'URL EXPORT
        url = api_url.UrlStats(integral=False)
        url.set_criteria('date_start=', date_start)
        url.set_criteria('date_end=', date_end)
        url.set_criteria('jurisdiction=', jurisdiction)
        try:
            self.connexion.send_request(url, internal=True)
        except exc.ERRORS as e:
            raise e
        except exc.NoResult:
            self._dict_lists[jurisdiction].append((label, "0"))
        else:
            dict_answer = self.connexion.dict_answers["internal"]
            results = dict_answer.dict_from_response["results"]
            self._dict_lists[jurisdiction].append(
                            (label,
                             "{:,}".format(results["total_decisions"])))

    def _get_data(self):
        "retourne les quatre listes pour construction des labels"
        final_list = list()
        for item in ["all", "cc", "ca", "tj", "tcom"]:
            final_list.append(self._dict_lists[item])
        return final_list
