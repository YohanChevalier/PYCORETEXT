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
Classes pour instanciation d'une page de résultat
"""

import tkinter as tk
from tkinter import ttk, VERTICAL
from pycoretext.api_controller import api_answers
from pycoretext.widgets import DecisionsList, ButtonWholeText


class ResultPage(tk.Frame):
    """
    Liste des résultats pour une recherche
    Hérité de Frame
    A insérer dans un notebook
    """

    def __init__(self, parent, answer: api_answers.Answer, *args, **kwargs):
        """
        initialisation de l'objet
        """
        super().__init__(parent, *args, **kwargs)
        # récupération des données importantes liées à l'answer
        self._answer = answer
        self._id_answer = answer.id_answer
        self._dict_criterias = answer.dict_criterias
        self._answer_type = self.identify_type(str(answer.__class__))
        if self._answer_type in ["export", "search"]:
            self._nb_decision = answer.total_decisions
            self.dict_decisions = answer.dict_decisions
        elif self._answer_type == "decision":
            self._nb_decision = str(1)
            self.decision = answer.decision.dict_meta
        elif self._answer_type == "taxonomy":
            if hasattr(self._answer, "list_results"):
                self.result_taxo = self._answer.list_results
            else:
                self.result_taxo = self._answer.dict_results
            self._nb_decision = None
        else:
            self._nb_decision = None
        # configuration du widget
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        # frame principal
        self._left_frame = ttk.Frame(self)
        self._left_frame.grid(row=0, column=0, sticky="eswn")
        self._left_frame.columnconfigure(0, weight=1)
        # ajout des critères et du nb de décisions si nécessaire
        self.add_answer_details()
        # construction des résultats selon le type de l'Answer
        if self._answer_type in ["export", "search"]:
            self.add_treeview()
            self.add_text()
            # on lie l'évènement <<DisplayDecision>>
            self._treeview.bind("<<DisplayDecision>>",
                                self.retrieve_selection_treeview)
        elif self._answer_type == "decision":
            self.add_text()
            self._feed_text(self.decision)
            self._build_access_text_button(
                self.decision["text"],
                self.decision["id"],
                self.decision["number"]
                )
        elif self._answer_type == "taxonomy":
            self.add_text()
            self._feed_text_from_taxonomy()

    def add_answer_details(self):
        """
        Affiche le dict_criteria ainsi que le nombre de décisions trouvé
        """
        # frame principal
        details_frame = ttk.Frame(self._left_frame)
        details_frame.grid(row=0, column=0, sticky=tk.W + tk.E,
                           pady=5, padx=5)
        details_frame.columnconfigure(0, weight=1)
        # fritères de recherche
        criteria_frame = ttk.LabelFrame(
            details_frame,
            text="Critères de recherche")
        criteria_frame.grid(row=0, column=0, sticky=tk.W + tk.E + tk.N,
                            pady=(0, 5))
        ttk.Label(
            criteria_frame,
            text=self._criteria_to_string()
            ).grid(row=0, column=0, sticky=tk.W + tk.E)
        # nombre de décisions trouvées si existe :
        if self._nb_decision:
            total_frame = ttk.LabelFrame(
                details_frame,
                text="Nombre de décisions")
            total_frame.grid(row=1, column=0, sticky=tk.W + tk.E + tk.N)
            ttk.Label(
                total_frame,
                text=self._nb_decision
                ).grid(row=0, column=0, sticky=tk.W + tk.E)

    def add_treeview(self):
        """
        Construit le treeview si plusieurs décisions ont été renvoyées
        """
        self._treeview = DecisionsList(self._left_frame)
        self._treeview.grid(row=1, column=0, sticky=tk.W + tk.E + tk.N + tk.S,
                            padx=5, pady=(0, 5))
        self._treeview.populate(self.dict_decisions)

    def add_text(self):
        """
        Construit la fenêtre de visualisation des métadonnées
        """
        self._text = tk.Text(self, height=30, wrap="word")
        self._text.grid(row=0, column=1, sticky=tk.E + tk.W + tk.N + tk.S,
                        padx=5, pady=5)
        # création de la scrollbar
        s = ttk.Scrollbar(self, orient=VERTICAL,
                          command=self._text.yview)
        s.grid(row=0, column=2, sticky=tk.N + tk.S + tk.W)
        self._text["yscrollcommand"] = s.set

    def retrieve_selection_treeview(self, *_):
        """
        Récupère la sélection d'un treeview et appelle self._feed_text
        """
        # decision sélectionnée
        selection = self._treeview.selected_id
        dict_meta = self.dict_decisions[selection].dict_meta
        self._feed_text(dict_meta)
        if self._answer_type == "export":
            self._build_access_text_button(
                dict_meta["text"],
                dict_meta["id"],
                dict_meta["number"])

    def _feed_text(self, dict_meta: dict):
        """
        Ecrit les éléments d'un dictionnaire donné dans le widget self._text
        Pour Export, Search et Decision
        """
        self._text.delete("1.0", tk.END)
        # classement alphabétique des métadonnées
        sorted_keys = sorted(list(dict_meta.keys()))
        count_line = 1.0
        for key in sorted_keys:
            # on gère le texte ailleurs
            if key != "text":
                value = dict_meta[key]
                self._text.insert(
                    str(count_line), f'==== {key.upper()} ====\n')
                count_line += 1
                count_line = self._write_value_in_text(value, count_line)
                self._text.insert(str(count_line), '\n\n')
                count_line += 1

    def _write_value_in_text(self, value, count_line: float):
        """
        Ecrit dans self._text la valeur donnée selon son type et son contenu.
        """
        # Liste
        if isinstance(value, list):
            if not len(value):
                self._text.insert(str(count_line), "None")
                count_line += 1
            # Liste de string = string séparée par " / "
            elif isinstance(value[0], str):
                self._text.insert(str(count_line), " / ".join(value))
                count_line += 1
            # Liste de dict = string débutant par # et avec saut de ligne
            elif isinstance(value[0], dict):
                for index_list, item in enumerate(value):
                    ch = ""
                    for index_dict, key in enumerate(list(item.keys())):
                        v = item[key]
                        if isinstance(v, str):
                            v = v.replace("\n", " ")
                        ch += f"{key.capitalize()} : {v}"
                        if index_dict + 1 < len(list(item.keys())):
                            ch += ", "
                    self._text.insert(str(count_line), f"# {ch}")
                    count_line += 1
                    if index_list + 1 < len(value):
                        self._text.insert(str(count_line), '\n')
                        count_line += 1
        # Dictionnaire = string débutant par #
        elif isinstance(value, dict):
            if not len(value):
                self._text.insert(str(count_line), "None")
                count_line += 1
            else:
                ch = ""
                for index, key in enumerate(list(value.keys())):
                    v = value[key]
                    if isinstance(v, str):
                        v = v.replace("\n", " ")
                    ch += f"{key.capitalize()} : {v}"
                    if index + 1 < len(list(value.keys())):
                        ch += ", "
                self._text.insert(str(count_line), f"# {ch}")
                count_line += 1
        # String simple = pas de mise en forme particulière
        elif isinstance(value, str):
            value = value.split("\n")
            for line in value:
                self._text.insert(str(count_line), line)
                count_line += 1
        # Si boolean
        elif isinstance(value, bool):
            if value:
                self._text.insert(str(count_line), "Oui")
                count_line += 1
            else:
                self._text.insert(str(count_line), "Non")
                count_line += 1
        # Si Faux alors on écrit "None"
        else:
            self._text.insert(str(count_line), "None")
            count_line += 1
        # On renvoit le compteur de ligne pour continuer à alimenter self._text
        return count_line

    def _feed_text_from_taxonomy(self):
        """
        Affiche les résultats de taxonomy dans le widget text
        le résultat de taxonomy peut être un liste ou un dict
        """
        self._text.delete("1.0", tk.END)
        count_line = 1.0
        if isinstance(self.result_taxo, list):
            for value in self.result_taxo:
                self._text.insert(str(count_line), f'{value}')
                count_line += 1
                self._text.insert(str(count_line), '\n')
                count_line += 1
        else:
            for key, value in self.result_taxo.items():
                self._text.insert(str(count_line), f'=== {key} ===\n')
                count_line += 1
                self._text.insert(str(count_line), f'{value}')
                count_line += 1
                self._text.insert(str(count_line), '\n')
                count_line += 1

    def _build_access_text_button(self, decision_text,
                                  id_decision, number_decision):
        """
        Crée un widget ButtonWholeText pour afficher le texte de la décision
        """
        if hasattr(self, "access_text_button"):
            self.access_text_button.destroy()
        self.access_text_button = ButtonWholeText(
            self,
            decision_text,
            id_decision,
            number_decision
                )
        self.access_text_button.grid(
            row=1,
            column=1,
            sticky=tk.W + tk.E,
            padx=5, pady=5
        )

    def _criteria_to_string(self):
        """
        Prend le dictionnaire des critères et renvoit une string
        """
        final_string = ""
        list_keys = sorted(list(self._dict_criterias.keys()))
        for index, key in enumerate(list_keys):
            value = ""
            _l = len(self._dict_criterias[key])
            for i, item in enumerate(self._dict_criterias[key]):
                value += item
                if not i + 1 == _l:
                    value += " -"
            final_string += f"{key} {value}"
            if index in [3, 7, 11]:
                final_string += "\n"
            else:
                final_string += " | "
        return final_string

    def identify_type(self, class_name: str):
        """
        retourne le type de l'URL selon le nom de la classe URL
        """
        if "Export" in class_name:
            return "export"
        elif "Search" in class_name:
            return "search"
        elif "Decision" in class_name:
            return "decision"
        elif "Taxonomy" in class_name:
            return "taxonomy"
        else:
            return None
