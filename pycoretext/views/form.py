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
Module contenant la classe pour construire le bloc de la homepage qui
permettra de faire sélectionner des critères et de lancer des recherches
"""

import tkinter as tk
from tkinter import ttk
from pycoretext import widgets as w
from pycoretext.api_controller import api_url, api_connexion as co
from pycoretext import exceptions as exc


class SearchBloc(ttk.Labelframe):
    """
    Frame principal qui contiendra les sous_frames de la recherche
    """

    def __init__(self, master, connexion, text="RECHERCHE", *args, **kwargs):
        """
        Fonction d'initialisation
        """
        super().__init__(master=master, text=text, *args, **kwargs)
        # récupération de la connexion qui sera utile pour SearchData
        self.connexion = connexion
        # sauvegarde de l'ensemble des objets Var
        # la clé correpond aux critères de recherche
        # ils sont séparés par un espace
        self._vars = {
            "id": tk.StringVar(),
            "query": tk.StringVar(),
            "operator": tk.StringVar(),
            "chamber": tk.StringVar(),
            "formation": tk.StringVar(),
            "theme": tk.StringVar(),
            "theme ca": tk.StringVar(),
            "type": tk.StringVar(),
            "publication": tk.StringVar(),
            "solution": tk.StringVar(),
            "jurisdiction": tk.StringVar(),
            "date_start": tk.StringVar(),
            "date_end": tk.StringVar(),
            "date_type": tk.StringVar(),
            "idT": tk.StringVar(),
            "key": tk.StringVar(),
            "value": tk.StringVar(),
            "context_value": tk.StringVar(),
            "location ca": tk.StringVar()
        }
        # récupérer les données dynamiquement pour les inputs
        try:
            self._data = SearchData(self.connexion).data
        except exc.ERRORS as e:
            raise e
        else:
            self._create_form()

    def _create_form(self):
        """
        Construit le formulaire
        """
        # définition des groupes de widgets pour la gestion de la configuration
        decision = self._group_var(["id"])
        search_query = self._group_var(["query", "operator"])
        export_and_search = self._group_var([
                   "chamber", "formation", "theme", "theme ca",
                   "type", "publication", "solution", "jurisdiction",
                   "date_start", "date_end", "date_type", "location ca"
                   ])
        export_date_type = self._group_var(["date_type"])
        taxo = self._group_var(["idT", "key", "value", "context_value"])
        taxo_value = self._group_var(["value"])
        taxo_key = self._group_var(["key"])
        simple_and_critere = ttk.Frame(self)
        simple_and_critere.grid(column=0, row=0, sticky=tk.W)

        # RECHERCHE SIMPLE
        self._simple = ttk.LabelFrame(
            simple_and_critere, text="Recherche simple"
        )
        self._simple.grid(column=0, row=0, sticky=tk.N, padx=(0, 10))
        w.LabelInput(
            self._simple, "ID Judilibre", self._vars["id"],
            input_class=ttk.Entry,
            disable_vars=search_query+export_and_search+export_date_type+taxo
            ).grid(row=0, column=0)

        # RECHERCHE DES CRITÈRES
        self._taxo_frame = ttk.LabelFrame(
            simple_and_critere, text="Taxonomie : recherche des termes"
        )
        self._taxo_frame.grid(column=1, row=0, sticky=tk.W + tk.E)
        w.LabelInput(
            self._taxo_frame, "Métadonnée", var=self._vars["idT"],
            input_args={"items_list": self._data["idT"],
                        "heigh": 5, "selectmode": tk.SINGLE},
            disable_vars=(decision + export_and_search +
                          export_date_type + search_query)
        ).grid(row=0, column=0)
        w.LabelInput(
            self._taxo_frame, "Abréviation", var=self._vars["key"],
            input_class=ttk.Entry,
            disable_vars=(decision + export_and_search +
                          export_date_type + search_query + taxo_value)
        ).grid(row=0, column=1)
        w.LabelInput(
            self._taxo_frame, "Intitulé complet", var=self._vars["value"],
            input_class=ttk.Entry,
            disable_vars=(decision + export_and_search +
                          export_date_type + search_query + taxo_key)
        ).grid(row=0, column=2)
        w.LabelInput(
            self._taxo_frame, "Contexte", var=self._vars["context_value"],
            input_args={
                "items_list": ["cc", "ca"],
                "heigh": 2,
                "selectmode": tk.SINGLE},
            disable_vars=(decision + export_and_search +
                          export_date_type + search_query)
        ).grid(row=0, column=3)

        # RECHERCHE COMBINÉE
        self._combine = ttk.LabelFrame(
            self, text="Recherche combinée"
        )
        self._combine.grid(column=0, row=1, sticky=tk.W + tk.E)
        w.LabelInput(
            self._combine, "Mot(s) clé(s)", var=self._vars["query"],
            input_class=ttk.Entry,
            disable_vars=decision+export_date_type+taxo
        ).grid(row=0, column=0)
        w.LabelInput(
            self._combine, "Opérateur (df='or')",
            var=self._vars["operator"],
            input_args={
                "items_list": self._data["operator"],
                "heigh": 3,
                "selectmode": tk.SINGLE},
            disable_vars=decision+export_date_type+taxo
        ).grid(row=0, column=1)
        w.LabelInput(
            self._combine, "Du (AAAA-MM-JJ)", var=self._vars["date_start"],
            input_class=ttk.Entry,
            disable_vars=decision+taxo
        ).grid(row=0, column=2)
        w.LabelInput(
            self._combine, "Au (AAAA-MM-JJ)", var=self._vars["date_end"],
            input_class=ttk.Entry,
            disable_vars=decision+taxo
        ).grid(row=0, column=3)
        w.LabelInput(
            self._combine, "Type de date", var=self._vars["date_type"],
            input_args={"items_list": ["creation", "update"],
                        "heigh": 2},
            disable_vars=decision+taxo+search_query
        ).grid(row=0, column=4)
        w.LabelInput(
            self._combine, "Juridiction (df='cc')",
            var=self._vars["jurisdiction"],
            input_args={"items_list": self._data["jurisdiction"], "heigh": 2},
            disable_vars=decision+taxo
        ).grid(row=0, column=5)
        w.LabelInput(
            self._combine,
            label="Chambre", var=self._vars["chamber"],
            input_args={"items_list": self._data["chamber"],
                        "heigh": 6},
            disable_vars=decision+taxo
        ).grid(row=1, column=0)
        w.LabelInput(
            self._combine, "Formation", var=self._vars["formation"],
            input_args={"items_list": self._data["formation"],
                        "heigh": 6},
            disable_vars=decision+taxo
        ).grid(row=1, column=1)
        w.LabelInput(
            self._combine, "Nature de la décision", var=self._vars["type"],
            input_args={"items_list": self._data["type"],
                        "heigh": 6},
            disable_vars=decision+taxo
        ).grid(row=1, column=2)
        w.LabelInput(
            self._combine, "Publication", var=self._vars["publication"],
            input_args={"items_list": self._data["publication"],
                        "heigh": 5},
            disable_vars=decision+taxo
        ).grid(row=1, column=3)
        w.LabelInput(
            self._combine, "Solution", var=self._vars["solution"],
            input_args={"items_list": self._data["solution"],
                        "heigh": 6},
            disable_vars=decision+taxo
        ).grid(row=1, column=4)
        w.LabelInput(
            self._combine, "Siège ca", var=self._vars["location ca"],
            input_args={"items_list": self._data["location ca"],
                        "heigh": 6},
            disable_vars=decision+taxo
        ).grid(row=1, column=5)

        # les deux sélections pour les thèmes
        selections_frame = ttk.Frame(self._combine)
        selections_frame.grid(column=0, row=2, sticky=tk.W + tk.E,
                              columnspan=10)
        selections_frame.columnconfigure(0, weight=1)
        selections_frame.columnconfigure(1, weight=1)
        # thèmes CC
        self._select1 = w.LabelInput(
            selections_frame, "Matière cc", var=self._vars["theme"],
            input_class=w.ButtonSelect,
            input_args={"items_list": self._data["theme"]},
            disable_vars=decision+taxo)
        self._select1.grid(row=0, column=0, sticky=tk.E + tk.W)
        # thèmes CA
        self._select2 = w.LabelInput(
            selections_frame, "Matière ca", var=self._vars["theme ca"],
            input_class=w.ButtonSelect,
            input_args={"items_list": self._data["theme ca"]},
            disable_vars=decision+taxo)
        self._select2.grid(row=0, column=1, sticky=tk.W + tk.E)

        # création des boutons "Recherche" et "Reset"
        buttons_frame = ttk.LabelFrame(self, text="Actions")
        buttons_frame.grid(column=0, row=3, sticky=tk.W + tk.E)
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        # la commande du bouton de recherche est liée à une méthode
        # du module Application, le root.
        self._save_bouton = ttk.Button(
                    buttons_frame, text="Recherche",
                    command=self._on_search
                    )
        self._save_bouton.grid(row=0, column=0, sticky=tk.W + tk.E)
        # on lie la commande _on_search aux widgets avec <Return> en évènement
        self._bind_widgets_to_search()
        # reset
        self._reset_button = ttk.Button(buttons_frame,
                                        text="Effacer les critères",
                                        command=self._reset)
        self._reset_button.grid(row=0, column=1, sticky=tk.W + tk.E)

    def _on_search(self, *_):
        """
        Génère un événement de recherche pour l'application
        """
        # Génération d'un évènement à destination de l'application
        self.event_generate('<<OnSearch>>')

    def get(self):
        """
        Méthode qui permet de récupérer les informations du formulaire
        """
        # nouveau dictionnaire à retourner
        data_in_form = dict()
        # on récupère les données des variables. Seulement si complétée
        for key, value in self._vars.items():
            if value.get():
                data_in_form[key] = value.get()
        return data_in_form

    def _reset(self):
        """
        Remet à zéro tous les champs
        """
        for var in self._vars.values():
            # ce cas n'existe pas encore mais prévoyance
            if isinstance(var, tk.BooleanVar):
                var.set(False)
            else:
                var.set("")
        # vider les textes pour les ButtonSelect
        # vider les variables de sélection pour les ButtonSelect
        self._select1.input.text["state"] = "normal"
        self._select1.input.text.delete("1.0", tk.END)
        self._select1.input.text["state"] = "disabled"
        self._select1.input.selection = []
        self._select2.input.text["state"] = "normal"
        self._select2.input.text.delete("1.0", tk.END)
        self._select2.input.text["state"] = "disabled"
        self._select2.input.selection = []

    def _group_var(self, keys: list):
        """
        A partir d'une liste de clés extraites de self._vars,
        création d'une la liste de variables correspondantes
        """
        new_group = list()
        for key in keys:
            new_group.append(self._vars[key])
        return new_group

    def _bind_widgets_to_search(self):
        """
        On identifie les widgets inputs pour les lier à la commande de
        recherche
        """
        # Liste des frames contenant les widgets
        widgets_list = (self._simple.winfo_children() +
                        self._taxo_frame.winfo_children() +
                        self._combine.winfo_children())
        # bind en tenant compte de la particularité de l'objet LabelInput
        for widget in widgets_list:
            if hasattr(widget, "input"):
                if isinstance(widget.input, ttk.Entry):
                    widget.input.bind("<Return>", self._on_search)
                elif isinstance(widget.input, ttk.Frame):
                    if isinstance(widget.input.winfo_children()[0],
                                  tk.Listbox):
                        widget.input.winfo_children()[0].bind(
                                        "<Return>", self._on_search)


class SearchData:
    """
    objet collectant les critères de recherche pour le formulaire grâce
    à différentes méthodes
    """
    def __init__(self, connexion: co.Connexion):
        """
        Fonction d'initialisation
        """
        self.connexion = connexion
        main_list = self._create_main_list()
        # variables qui contiendront les listes des critères
        self.data = {
            "chamber": self._create_sub_list("chamber"),
            "formation": self._create_sub_list("formation"),
            "theme": self._create_sub_list("theme"),
            "theme ca": self._create_sub_list("theme ca"),
            "type": self._create_sub_list("type"),
            "publication": self._create_sub_list("publication"),
            "solution": self._create_sub_list("solution"),
            "jurisdiction": self._create_sub_list("jurisdiction"),
            "operator": self._create_sub_list("operator"),
            "idT": main_list,
            "location ca": self._create_sub_list("location ca")
        }
        # vider le dictionnaire
        self.connexion.dict_answers.clear()

    def _create_main_list(self):
        """
        Crée la liste principale des critères
        """
        all_criteria_url = api_url.UrlTaxonomy()
        # critère "id=" mais pas de valeur pour avoir la totale
        all_criteria_url.set_criteria("id=", "")
        try:
            self.connexion.send_request(all_criteria_url, internal=True)
        except exc.ERRORS as e:
            raise e
        else:
            # on supprime les valeurs sans intérêt
            to_return = self.connexion.dict_answers["internal"].list_results
            to_return.remove("cc")
            to_return.remove("ca")
            to_return.remove("all")
            return to_return

    def _create_sub_list(self, criteria: str):
        """
        Crée la liste pour un ou plusieurs critères définis
        """
        # création de l'ojet URL
        criteria_url = api_url.UrlTaxonomy()
        # le cas échéant, id et context_value séparés par un espace
        # il faut le gérer :
        if " " in criteria:
            list_criterias = criteria.split(" ")
            criteria_url.set_criteria("id=", list_criterias[0])
            criteria_url.set_criteria("context_value=", list_criterias[1])
        else:
            criteria_url.set_criteria("id=", criteria)
        # On récupère les données
        try:
            self.connexion.send_request(criteria_url, internal=True)
        except exc.ERRORS as e:
            raise e
        else:
            # les thèmes sont liés soit au cc, soit au ca = tri à effectuer
            if criteria == "theme":
                data = self.connexion.dict_answers["internal"].list_results
            elif criteria == "theme ca":
                # les thèmes ca ne sont pas encore correctement gérées par
                # l'API. Suivre les améliorations pour ajuster les dev.
                data = []
                for key, values in (
                        self.connexion.dict_answers["internal"].
                        dict_results.items()):
                    # on met en valeur les dés entre des astérisques
                    data.append("**" + str(key) + "**")
                    # on poursuit avec les autres valeurs
                    for value in values:
                        data.append(value)
            # dans tous les autres cas :
            else:
                data = list(
                    self.connexion.dict_answers["internal"].dict_results.keys()
                           )
            return data
