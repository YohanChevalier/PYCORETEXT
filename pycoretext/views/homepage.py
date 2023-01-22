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

import tkinter as tk
from tkinter import ttk
from datetime import date as d, timedelta as td
from pycoretext import exceptions as exc, widgets as w
from pycoretext.api_controller import api_url
from . import form


class Homepage(ttk.Frame):
    """
    Entité principale de la homepage, héritée du widget Frame
    """

    def __init__(self, parent, connexion, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # paramétrage de la fenêtre homepage
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)

        # création du bloc pour les parties informatives
        left_frame = tk.Frame(self)
        left_frame.grid(column=0, row=0, sticky=tk.W + tk.E + tk.N + tk.S)
        left_frame.columnconfigure(0, weight=1)
        # création du bloc d'infos
        try:
            service_state = InfosBlocData(connexion)._get_data()
        except exc.ERRORS as e:
            raise e
        else:
            infos = InfosBloc(
                left_frame, "Infos", connexion.endpoint,
                connexion.key_user, service_state)
            infos.grid(
                column=0, row=0, sticky=tk.W + tk.E,
                pady=(0, 10), padx=8)
            # création du bloc des statistiques judilibre
            try:
                stats = StatsBloc(
                    left_frame, "Statistiques Judilibre",
                    StatsBlocData(connexion)._get_data())
                stats.grid(
                    column=0, row=1, sticky=tk.W + tk.E, padx=8)
            except exc.ERRORS as e1:
                raise e1
            else:
                # création du formulaire de recherche
                try:
                    self.search = form.SearchBloc(self, connexion)
                    self.search.grid(column=1, row=0, sticky=tk.W + tk.E)
                    self.search.columnconfigure(0, weight=1)
                    self.search.columnconfigure(1, weight=1)
                except exc.ERRORS as e:
                    raise e


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
    def __init__(self, master, text: str, data: tuple, *args, **kwargs):
        """
        fonction d'initialisation
        """
        super().__init__(master=master, text=text, *args, **kwargs)
        # configuration des colonnes
        self.columnconfigure(0, weight=1)
        # liste des labels à utiliser pour le widget double_labels
        self._data = data
        # liste des labels d'entête pour les sous-frames
        titles_frames = ["Général", "Cour de cassation", "Cours d'appel"]
        # liste des LabelFrame widget
        labels_list = list()
        # création des sous-frames et des labels à l'intérieur
        for i in range(3):
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
        self._all_list = list()
        self._cc_list = list()
        self._ca_list = list()
        # compléter les listes
        self._build_lists()

    def _build_lists(self):
        """
        Complète les listes _all, _cc, et _ca puis les retourne
        """
        # 1/ collecter les infos en provenance de la commande STATS (interne)
        try:
            self.connexion.send_request(api_url.UrlStats(), internal=True)
        except exc.ERRORS as e:
            raise e
        else:
            stats_dict_meta = self.connexion.dict_answers["internal"].dict_meta
            self._all_list.append(("Nb total des textes",
                                  "{:,}".format(
                                            stats_dict_meta["indexedTotal"])))
            self._all_list.append(("Date créa. la plus récente",
                                  stats_dict_meta["newestDecision"]))
            self._cc_list.append(("Nb textes",
                                  "{:,}".format(stats_dict_meta[
                                    "indexedByJurisdiction"][0]["value"])))
            self._ca_list.append(("Nb textes",
                                  "{:,}".format(stats_dict_meta[
                                    "indexedByJurisdiction"][1]["value"])))
            # 2/ autres requêtes personnalisées avec la commande EXPORT
            # (interne) constantes pour les requêtes :
            today = d.today()
            diff1 = td(days=1)
            yesterday = today - diff1
            month = str(today.month)
            first_day_month = today.replace(day=1)
            last_day_of_prev_month = today.replace(day=1) - td(days=1)
            start_day_of_prev_month = today.replace(day=1) - td(
                                            days=last_day_of_prev_month.day)
            previous_month = last_day_of_prev_month.month
            # requêtes pour chaque organisme
            for orga in ["cc", "ca"]:
                self._date_request(
                    "créés hier",
                    yesterday,
                    yesterday,
                    orga
                )
            for orga in ["cc", "ca"]:
                self._date_request(
                    f"Créés mois en cours ({str(month)})",
                    first_day_month,
                    today, orga
                )
            for orga in ["cc", "ca"]:
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
        url = api_url.UrlExport(integral=False)
        url.set_criteria('date_start=', date_start)
        url.set_criteria('date_end=', date_end)
        url.set_criteria('jurisdiction=', jurisdiction)
        try:
            self.connexion.send_request(url, internal=True)
        except exc.ERRORS as e:
            raise e
        except exc.NoResult:
            if jurisdiction == "cc":
                self._cc_list.append((label, "0"))
            else:
                self._ca_list.append((label, "0"))
        else:
            if jurisdiction == "cc":
                self._cc_list.append((
                    label,
                    "{:,}".format(self.connexion.
                                  dict_answers["internal"].total_decisions)))
            else:
                self._ca_list.append((
                    label,
                    "{:,}".format(self.connexion.
                                  dict_answers["internal"].total_decisions)))

    def _get_data(self):
        "retourne les trois listes pour construction des labels"
        return (self._all_list, self._cc_list, self._ca_list)
