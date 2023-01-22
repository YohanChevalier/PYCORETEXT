# Création de la connexion puis ajout de 2 objets answers
from pycoretext.api_controller import api_connexion
from pycoretext.api_controller import api_url
import tkinter as tk
from tkinter import ttk


class DecisionsList(tk.Frame):
    """Widget treeview pour afficher le résultat de la recherche"""

    # Définition anticipée des colonnes et de leur configuration
    columns_def = {
        "#0": {"label": "ID", "width": 40},
        "jurisdiction": {"label": "Jur", "width": 30},
        "type": {"label": "Nat"},
        "decision_date": {"label": "Date", "width": 80},
        "number": {"label": "Num", "width": 70},
        "chamber": {"label": "Ch", "width": 50},
        "publication": {"label": "Pub", "width": 40},
    }
    default_width = 70
    default_minwidth = 10
    default_anchor = tk.W

    def __init__(self, parent, *args, **kwargs):
        """A déterminer"""
        super().__init__(parent, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        # création du treeview
        self.treeview = ttk.Treeview(
            self,
            columns=list(self.columns_def.keys())[1:],
            selectmode="browse"
        )
        self.treeview.grid(row=0, column=0, sticky=tk.W + tk.E + tk.N + tk.S)
        # configuration des headings du treeview à partir du columns_def dict
        for name, definition in self.columns_def.items():
            label = definition.get("label", "")
            anchor = definition.get("anchor", self.default_anchor)
            minwidth = definition.get("minwidth", self.default_minwidth)
            width = definition.get("width", self.default_width)
            stretch = definition.get("stretch", False)
            self.treeview.heading(name, text=label, anchor=anchor)
            self.treeview.column(
                name, anchor=anchor, minwidth=minwidth,
                width=width, stretch=stretch
            )
        # gestion des évènements de sélection
        # double clic ou bouton entrée affichera la décision
        self.treeview.bind('<Double-1>', self._on_display_decision)
        self.treeview.bind('<Return>', self._on_display_decision)
        # ajout d'une scrollbar
        self.scrollbar = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.treeview.yview
        )
        self.treeview.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky=tk.W + tk.E + tk.N + tk.S)

    def _on_display_decision(self, *args):
        """génère un évènement particulier qui sera utilisé par l'app"""
        self.event_generate("<<DisplayDecision>>")

    @property
    def selected_id(self):
        """retourne l'ItemID de l'élément sélectionné dans le treeview"""
        selection = self.treeview.selection()
        # treeview.selection() retourne toujours une liste
        # on prend le 1er élément
        return int(selection[0]) if selection else None

    def populate(self, dict_decision: dict):
        """Vide le treeview et ajoute les lignes nécessaires
        dict_decisions correspond à un dictionnaire de décisions fourni
        par l'objet Answer
        """
        # on récupère la liste des colonnes définies pour notre treeview
        cids = self.treeview.cget('columns')
        # pour chaque décision
        for key, value in dict_decision.items():
            # on récupère son dictionnaire de méta
            dict_meta = value.dict_meta
            values = [dict_meta[cid] for cid in cids]
            self.treeview.insert("", "end", iid=str(key),
                                 text=str(key), values=values)
        # On place la sélection sur le premier élément de la liste
        # "1" car nous idenfions les décisions à partir de 1 dans Answer
        self.treeview.focus_set()
        self.treeview.selection_set("1")
        self.treeview.focus("1")


if __name__ == "__main__":
    # Connexion
    co = api_connexion.Connexion()
    # URL pour le test
    # url_search = api_url.UrlSearch("boulangerie")
    # url_search.set_criteria("type=", "arret")
    # url_search.set_criteria("publication=", "b")
    url_export = api_url.UrlExport()
    url_export.set_criteria("type=", "arret")
    url_export.set_criteria("date_start=", "2019-10-15")
    url_export.set_criteria("date_end=", "2022-10-20")
    url_export.set_criteria("date_type=", "creation")

    # co.send_request(url_search)
    try:
        co.send_request(url_export)
    except Exception as e:
        print(e)
    else:
        print(co.dict_answers[1].__name__)

        root = tk.Tk()
        table = DecisionsList(root)
        table.pack()
        table.populate(co.dict_answers[1].dict_decisions)

        root.mainloop()
