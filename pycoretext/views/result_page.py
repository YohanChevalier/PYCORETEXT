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
from tkinter import ttk, VERTICAL, filedialog
import webbrowser as web
import pandas as pd
from datetime import datetime
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
            # Alerte si limite de recherche API atteinte (10 000)
            if self._nb_decision >= 10000:
                ttk.Label(total_frame, text="Limite API atteinte !",
                          foreground="red").grid(
                    row=0, column=1, sticky=tk.W + tk.E,
                    padx=10
                          )

    def add_treeview(self):
        """
        Construit le treeview si plusieurs décisions ont été renvoyées
        """
        self._treeview = DecisionsList(self._left_frame)
        self._treeview.grid(row=1, column=0, sticky=tk.W + tk.E + tk.N + tk.S,
                            padx=5)
        self._treeview.populate(self.dict_decisions)
        # Ajout du bouton pour export Excel
        self._button_excel = ttk.Button(self._left_frame, text="Export Excel brut",
                                        command=self._export_raw_excel)
        self._button_excel.grid(row=2, column=0,
                                sticky=tk.W + tk.E + tk.N,
                                padx=5, pady=(5, 1))

    def add_text(self):
        """
        Construit la fenêtre de visualisation des métadonnées
        """
        self._text = tk.Text(self, height=25, wrap="word")
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
        for key in sorted_keys:
            # on gère le texte ailleurs
            if key != "text":
                value = dict_meta[key]
                self._text.insert(
                    tk.END, f'==== {key.upper()} ====\n')
                self._write_value_in_text(value)
                self._text.insert(tk.END, '\n\n')

    def _write_value_in_text(self, value):
        """
        Ecrit dans self._text la valeur donnée selon son type et son contenu.
        """
        # Liste
        if isinstance(value, list):
            if not len(value):
                self._text.insert(tk.END, "None")
            # Liste de string = string séparée par " / "
            elif isinstance(value[0], str):
                self._text.insert(tk.END, " / ".join(value))
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
                    # Recherche des possibles hyperliens
                    # Obtention des indices des targets si des remplacements
                    # ont été faits
                    hyperlinks_info = self._find_replace_hyperlink(ch)
                    # Si des hyperliens ont été trouvés
                    if hyperlinks_info:
                        new_ch = hyperlinks_info[0]
                        self._text.insert(tk.END, f"# {new_ch}")
                        # dernière ligne complétée
                        i_line = self._text.index(
                                        "end - 1 chars").split('.')[0]
                        # Application des tag
                        for tag in hyperlinks_info[1]:
                            self._add_hypertags(i_line,
                                                tag[0] + 2,
                                                tag[1] + 2,
                                                tag[2])
                    else:
                        self._text.insert(tk.END, f"# {ch}")
                    if index_list + 1 < len(value):
                        self._text.insert(tk.END, '\n')
        # Dictionnaire = string débutant par #
        elif isinstance(value, dict):
            if not len(value):
                self._text.insert(tk.END, "None")
            else:
                ch = ""
                for index, key in enumerate(list(value.keys())):
                    v = value[key]
                    if isinstance(v, str):
                        v = v.replace("\n", " ")
                    ch += f"{key.capitalize()} : {v}"
                    if index + 1 < len(list(value.keys())):
                        ch += ", "
                self._text.insert(tk.END, f"# {ch}")
        # String simple = pas de mise en forme particulière
        elif isinstance(value, str):
            value = value.split("\n")
            for line in value:
                self._text.insert(tk.END, line)
        # Si boolean
        elif isinstance(value, bool):
            if value:
                self._text.insert(tk.END, "Oui")
            else:
                self._text.insert(tk.END, "Non")
        # Si Faux alors on écrit "None"
        else:
            self._text.insert(tk.END, "None")

    def _feed_text_from_taxonomy(self):
        """
        Affiche les résultats de taxonomy dans le widget text
        le résultat de taxonomy peut être un liste ou un dict
        """
        self._text.delete("1.0", tk.END)
        if isinstance(self.result_taxo, list):
            for value in self.result_taxo:
                self._text.insert(tk.END, f'{value}')
                self._text.insert(tk.END, '\n\n')
        else:
            for key, value in self.result_taxo.items():
                self._text.insert(tk.END, f'=== {key} ===\n')
                self._text.insert(tk.END, f'{value}')
                self._text.insert(tk.END, '\n\n')

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

    def _find_replace_hyperlink(self, text):
        """
        Dans un texte :
        Trouve les balises <a></a> qui contiennent
        les attributs href et target
        Pour chaque occurence:
        /1 remplace <a></a> par la target (texte d'affichage)
        /2 conserve les indices de début et
        fin de la target dans le nouveau texte
        Retourne un tuple composé du nouveau text et d'une liste de tuples :
            -> Chaque tuple contient l'indice de début et
               de fin de la target ainsi que l'URL
        Si aucune balise <a></a> alors retourne None
        """
        is_there_hyperlink = False
        indices_and_url = []
        while 1:
            # Trouver le premier <a> dans le texte
            indice_start = text.find("<a")
            if indice_start == -1:
                break
            else:
                is_there_hyperlink = True
                indice_end = text.find("</a")
                hyper = text[indice_start:indice_end+4]
                url = hyper[hyper.find("https"):hyper.find("target")]
                target = hyper[hyper.find(">")+1:hyper.find("</a>")]
                text = text[:indice_start] + target + text[indice_end + 4:]
                i_start_targed_in_new_text = indice_start
                i_end_target_in_new_text = indice_start + len(target)
                indices_and_url.append((i_start_targed_in_new_text,
                                        i_end_target_in_new_text,
                                        url))
        if is_there_hyperlink:
            return (text, indices_and_url)
        else:
            return None

    def _open_url(self, url):
        """
        Ouvre l'URL donnée dans un nouvel onglet
        du navigateur défini par défaut"""
        web.open_new_tab(url)

    def _enter(self, event):
        """
        Change la forme du curseur en main"""
        self._text.config(cursor="hand2")

    def _leave(self, event):
        """
        Revient à la forme de curseur normal"""
        self._text.config(cursor="")

    def _add_hypertags(self, i_line, i_start, i_end, url):
        """
        Crée un tag sur un extrait de texte
        Le configure en bleu souligné
        Le bind à _leave et _enter pour la forme du curseur
        Le bind à _open_url"""
        # ajouter un tag (début et fin)
        self._text.tag_add(url, i_line + '.' + str(i_start),
                           i_line + '.' + str(i_end))
        # Le configurer en prenant l'url pour nom de tag
        self._text.tag_config(url, foreground="blue", underline=True)
        # Le lier à une méthode ou fonction
        self._text.tag_bind(url, "<Button-1>",
                            func=lambda event, url=url: self._open_url(url))
        self._text.tag_bind(url, "<Enter>", self._enter)
        self._text.tag_bind(url, "<Leave>", self._leave)

    def _export_raw_excel(self):
        """
        Méthode qui utilise Pandas pour exporter
        les données dans Excel"""
        # dictionnaire adapté à Pandas
        dict_for_export = {}
        for key, value in self.dict_decisions.items():
            # copie du dictionnaire de la décision
            meta_in_value = value.dict_meta.copy()
            dict_for_export[key] = meta_in_value
            # suppression du text
            dict_for_export[key].pop("text")
        # création du dataframe transposé
        df = pd.DataFrame(dict_for_export).T
        today = datetime.today().strftime("%Y-%m-%d")
        filename = f"\\{today}_pycoretext_export.xlsx"
        # on demande à l'utilisateur dans quel dossier placer le fichier excel
        export_path = filedialog.askdirectory()
        # export Excel
        df.to_excel(export_path + filename)
