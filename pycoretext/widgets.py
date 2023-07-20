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
Ce module contient les créations de classes de widgets pour pycoretext
"""

import tkinter as tk
from tkinter import ttk, VERTICAL, WORD


class DoubleLabel(ttk.Frame):
    """
    Un widget constitué d'une Frame avec deux Labels côte à côte
    """

    def __init__(self, parent, label1="", label2="", *args, **kwargs):
        """
        Fonction d'initialisation
        """
        super().__init__(parent, *args, **kwargs)
        # définition des polices
        font1 = ("tkDefaultFont", 9,)
        font2 = ("tkDefaultFont", 8,)
        # paramétrage du Frame
        self.grid(column=0, sticky=tk.W + tk.E)
        self.columnconfigure(1, weight=1)
        # creation du premier label
        ttk.Label(self, text=label1 + " :", font=font1).grid(
            column=0, row=1, sticky=tk.W + tk.E, padx=(5, 0)
            )
        # creation du second label
        ttk.Label(self, text=label2, font=font2).grid(
            column=1, row=1, sticky=tk.W + tk.E
            )


class LabelInput(tk.Frame):
    """
    Widget principal pour la construction du formulaire
    Il est constitué d'un Label et d'un widget d'input ()
    ex de widgets input : Entry, Listbox, Checkbox, Button, Radiobutton
    """

    def __init__(self, parent, label, var, input_class=tk.Listbox,
                 input_args=None, label_args=None,
                 disable_vars=None, **kwargs):
        """"
        Fonction d'initialisation de l'instance
        """
        super().__init__(parent, **kwargs)
        # si ces args sont None alors ils deviennent des dictionnaires
        # c'est la bonne méthode pour obtenir de nouveaux dictionnaires à
        # chaque initialisation. Si je l'avais mis dans la signature, j'aurais
        # toujours obtenu le même objet...
        input_args = input_args or {}
        label_args = label_args or {}
        # variable de contrôle tkinter
        self.variable = var
        # permettra de connaître les wigets à désactiver si ce LabelInput
        # est complété
        self.disable_vars = disable_vars or []
        # the Label input becomes a property of the variable
        # we can access to the object through the variable object if we need !
        self.variable.label_widget = self

        # # mise en place du label
        # checkbutton et button ont leur propre label intégré
        if input_class in [ttk.Checkbutton, ttk.Button]:
            input_args["text"] = label
        else:
            self.label = ttk.Label(self, text=label, **label_args)
            self.label.grid(row=0, column=0, sticky=(tk.W + tk.E))

        # # mise en place du contenu pour le widget input
        # le paramètre attendu pour la variable input peut avoir un nom
        # différent selon les widgets
        if input_class in (
            ttk.Checkbutton, ttk.Button, ttk.Radiobutton
        ):
            input_args["variable"] = self.variable
        # tk.Listbox n'attend pas d'argument de variable
        # Par contre, on ajoute un observateur qui enlevera
        # les sélections si la variable est vide
        elif input_class in [tk.Listbox]:
            self.variable.trace_add('write', lambda *_,
                                    var=self.variable: self._unselect(var))
        elif input_class == ButtonSelect:
            # Rien de spécial pour le ButtonSelect
            pass
        else:
            input_args["textvariable"] = self.variable

        # # mise en place du widget input lui-même
        # le Radiobutton est traité de manière particulière
        # -> les boutons seront dans un Frame
        # -> chaque valeur donnée devient un bouton
        # -> la clé "values" est supprimé du dict d'args car ce n'est pas un
        #    argument attendu par Radiobutton
        if input_class == ttk.Radiobutton:
            self.input = ttk.Frame(self)
            self.input.grid(row=1, column=0, sticky=(tk.W + tk.E))
            for i, v in enumerate(input_args.pop('values', [])):
                button = ttk.Radiobutton(
                    self.input, value=v, text=v, **input_args
                )
                button.grid(row=0, column=i)
        elif input_class == tk.Listbox:
            self.input = ttk.Frame(self)
            self.input.grid(row=1, column=0, sticky=(tk.W + tk.E))
            # ajout de l'option multivalues pour la liste
            if "selectmode" not in input_args:
                input_args["selectmode"] = tk.MULTIPLE
            # ajout d'une option pour que les sélections soient conservées
            # lorsque nous passons d'une liste à une autre
            input_args["exportselection"] = False
            # récupération de la liste d'items et suppression de inpup_args
            items_list = input_args.pop("items_list", [])
            # création du widget
            widget_list = tk.Listbox(self.input, **input_args)
            widget_list.grid(row=0, column=0)
            # bind l'input à une fonction de récupération des données
            widget_list.bind('<<ListboxSelect>>',
                             lambda event, widget=self: self._update(widget))
            # ajout des valeurs dans la listbox
            for i in items_list:
                widget_list.insert(tk.END, i)
            # création de la scrollbar
            s = ttk.Scrollbar(self.input, orient=VERTICAL,
                              command=widget_list.yview)
            s.grid(row=0, column=1, sticky=tk.N + tk.S)
            widget_list["yscrollcommand"] = s.set
        elif input_class == ButtonSelect:
            # pour ButtonSelect, ajout du label pour le titre de
            # la fenêtre top-level
            input_args["label_top"] = f"Sélection pour '{label}'"
            self.input = input_class(self, **input_args)
            self.input.grid(row=1, column=0, sticky=(tk.W + tk.E))
            self.columnconfigure(0, weight=1)
            # bind une fonction particulière à une sélection de valeur
            self.input.bind('<<on_button_select_validation>>',
                            self._on_new_selection)
        # les autres types de widget sont traiter normalement
        else:
            self.input = input_class(self, **input_args)
            self.input.grid(row=1, column=0, sticky=(tk.W + tk.E))
            self.columnconfigure(0, weight=1)

        # # mise en place des traces pour les variables
        # l'argument label dans la fonction lambda est optionnel mais
        # permet des tests si nécessaire
        if self.disable_vars:
            for widget in self.disable_vars:
                widget.trace_add(
                        'write',
                        lambda *_, label=label: self._check_disable(label)
                        )

    def grid(self, sticky=(tk.W + tk.N), padx=5, pady=5, **kwargs):
        """Overidde grid to add default sticky values"""
        super().grid(sticky=sticky, padx=padx, pady=pady, **kwargs)

    def _check_disable(self, label, *_):
        """
        Des observateurs ont été initialisés sur les variables données
        dans disable_vars. Chaque fois que l'une de ces variables est modifiée:
          1/ on vérifie si elle contient une valeur
          1/ on vérifie l'état du LabelInput actuel (DISABLED ou NORMAL)
          3/ on désactive ou active LabelInput en conséquence
        !! Mention spéciale pour Listbox et Radiobutton qui exige un traitement
        particulier. En effet, self.input est ttk.Frame qui n'a pas la capacité
        à être activé ou désactivé.
        => Il faut donc aller chercher les enfants de Frame.
        """
        # variable qui permettra de savoir si la variable vérifiée est
        # complétée ou non
        completed = False
        # variable qui contiendra le widget à activer ou désactiver
        input = None
        # placer ButtonSelect en premier dans ce bloc de conditions
        # il hérite de ttk.Frame alors si on le place après, le traitement
        # appliqué n'est pas conforme.
        if isinstance(self.input, ButtonSelect):
            # Variable qui contient le bouton
            input = self.input.button
            state = str(input['state'])
        elif isinstance(self.input, ttk.Frame):
            input = self.input.winfo_children()
            state = str(input[0]['state'])
        else:
            input = self.input
            state = str(input['state'])
        # l'une des variables est-elle complétée ?
        for var in self.disable_vars:
            if var.get():
                completed = True
                break
        # si oui :
        if completed:
            if state == "disabled":
                pass
            else:
                if isinstance(input, list):
                    if isinstance(input[0], ttk.Radiobutton):
                        for i in input:
                            i.configure(state=tk.DISABLED)
                        self.variable.set('')
                    elif isinstance(input[0], tk.Listbox):
                        input[0].configure(state=tk.DISABLED)
                elif isinstance(input, ttk.Button):
                    input.configure(state=tk.DISABLED)
                else:
                    input.configure(state=tk.DISABLED)
                    self.variable.set('')
        # si non :
        else:
            if state == "NORMAL":
                pass
            else:
                if isinstance(input, list):
                    if isinstance(input[0], ttk.Radiobutton):
                        for i in input:
                            i.configure(state=tk.NORMAL)
                        self.variable.set('')
                    elif isinstance(input[0], tk.Listbox):
                        input[0].configure(state=tk.NORMAL)
                else:
                    input.configure(state=tk.NORMAL)

    def _update(self, widget):
        """
        Méthode spécifique aux Listbox.
        Dès qu'une valeur est sélectionnée dans la liste
        elle est enregistrée dans la variable de contrôle de l'objet
        """
        # récupération de la sélection (tuple de chiffre débutant à 0)
        selection = widget.input.winfo_children()[0].curselection()
        to_return = []
        for i in selection:
            item = widget.input.winfo_children()[0].get(i, i)
            item = "".join(item)
            to_return.append(item)
        to_return = "/".join(to_return)
        # enregistrement de la sélection dans la variable
        widget.variable.set(to_return)

    def _unselect(self, var, *_):
        """
        Méthode spécifique aux Listbox.
        Tout est desélectionné si la variable est vide
        """
        if not var.get():
            self.input.winfo_children()[0].selection_clear(0, tk.END)

    def _on_new_selection(self, *_):
        """
        Méthode spécifique aux ButtonSelect.
        On alimente la variable de contrôle de l'objet
        """
        selection = self.input.selection
        selection = "/".join(selection)
        self.variable.set(selection)


class ButtonSelect(ttk.Frame):
    """
    Bouton qui permet d'ouvrir une fenêtre de niveau supérieur afin
    de proposer une ListBox grand format et des options de sélection
    """
    def __init__(self, parent, items_list=None,
                 label_top='Sélection', **kwargs):
        """
        Fonction d'initialisation de l'instance
        """
        super().__init__(parent, **kwargs)
        self._items_list = items_list or []
        # label du critère à mettre en titre du top-level
        self._label_top = label_top
        self.columnconfigure(0, weight=1)
        # variable qui récupère la sélection
        self.selection = []
        # variable qui mémorisera le widget Listbox
        self._widget_list = None
        # création du bouton
        self.button = ttk.Button(
            self, text="Sélectionner", command=self._selection_win
        )
        self.button.grid(row=0, column=0, sticky=tk.W + tk.E)
        # création du widget text qui affichera les choix sélectionnés
        self.text = tk.Text(self, width=50, height=6, wrap=WORD)
        self.text.grid(row=1, column=0, sticky=tk.W + tk.E)
        self.text["state"] = "disabled"
        # ajout d'une scrollbar sur le widget text
        s = ttk.Scrollbar(self, orient=VERTICAL,
                          command=self.text.yview)
        s.grid(row=1, column=1, sticky=tk.N + tk.S)
        self.text["yscrollcommand"] = s.set

    def _selection_win(self):
        """
        Construction d'une Listbox grand format
        """
        # top level window
        self.top = tk.Toplevel(self)
        self.top.columnconfigure(0, weight=1)
        self.top.title(self._label_top)
        # placement de la login page au centre de l'écran
        self._top_width = 1000
        self._top_height = 520
        self._screen_width = self.winfo_screenwidth()
        self._screen_height = self.winfo_screenheight()
        self._center_x = int(self._screen_width/2 - self._top_width / 2)
        self._center_y = int(self._screen_height/2 - self._top_height / 2)
        self.top.geometry(
            f'{self._top_width}x{self._top_height}' +
            f'+{self._center_x}+{self._center_y}')
        # frame principale
        top_frame = ttk.Frame(self.top)
        top_frame.grid(row=0, column=0, sticky=tk.W + tk.E)
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=1)
        top_frame.columnconfigure(2, weight=1)
        # frame pour la liste
        sub_frame = ttk.Frame(top_frame)
        sub_frame.grid(row=0, column=0, columnspan=3, sticky=tk.W + tk.E)
        sub_frame.columnconfigure(0, weight=1)
        # création de la liste
        self._widget_list = tk.Listbox(sub_frame, selectmode=tk.MULTIPLE,
                                       width=100, heigh=30)
        self._widget_list.grid(row=0, column=0, columnspan=2,
                               sticky=tk.W + tk.E)
        for item in self._items_list:
            self._widget_list.insert(tk.END, item)
        # scrollbar de la liste
        s = ttk.Scrollbar(sub_frame, orient=VERTICAL,
                          command=self._widget_list.yview)
        s.grid(row=0, column=1, sticky=tk.N + tk.S)
        self._widget_list["yscrollcommand"] = s.set
        # si la variable self._selection est déjà complétée alors
        # on sélectionne à nouveau les éléments
        if self.selection:
            for item in self.selection:
                index = self._widget_list.get(0, tk.END).index(item)
                self._widget_list.selection_set(index, index)
        # bouton de validation
        validate = ttk.Button(top_frame, text="Valider",
                              command=self._on_validate)
        validate.grid(row=1, column=0, sticky=tk.W + tk.E)
        # bouton pour tout déselectionner
        validate = ttk.Button(top_frame, text="Supprimer sélection",
                              command=self._on_delete)
        validate.grid(row=1, column=1, sticky=tk.W + tk.E)
        # bouton d'annulation => fermeture de la fenêtre
        cancel = ttk.Button(top_frame, text="Annuler",
                            command=self.top.destroy)
        cancel.grid(row=1, column=2, sticky=tk.W + tk.E)

    def _on_validate(self):
        """
        Méthode qui permet de récupérer la sélection de l'utilisateur au
        moment de la validation
        """
        # vider self.text
        self.text["state"] = "normal"
        self.text.delete("1.0", tk.END)
        # récupération de la sélection
        selection = self._widget_list.curselection()
        to_return = []
        if selection:
            for i in selection:
                item = self._widget_list.get(i, i)
                item = "".join(item)
                # On complète la liste à retourner
                to_return.append(item)
                # On complète aussi le widget text
                self.text.insert(tk.END, item + "\n")
        self.selection = to_return
        self.text["state"] = "disabled"
        # génération d'un événement qui sera géré par le LabelInput parent:
        self.event_generate('<<on_button_select_validation>>')
        self.top.destroy()

    def _on_delete(self):
        "retire sélection dans Listbox/vide self._selection/vide self.text"
        self._widget_list.selection_clear(0, tk.END)


class DecisionsList(tk.Frame):
    """
    Widget treeview pour afficher le résultat de la recherche
    """

    # définition anticipée des colonnes et de leur configuration
    columns_def = {
        "#0": {"label": "ID"},
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
        """
        Fonction d'initialisation
        """
        super().__init__(parent, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        # création du treeview
        self.treeview = ttk.Treeview(
            self,
            columns=list(self.columns_def.keys())[1:],
            selectmode="browse",
            height=18
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
        """
        Génère un évènement particulier qui sera utilisé par l'application
        """
        self.event_generate("<<DisplayDecision>>")

    @property
    def selected_id(self):
        """
        Retourne l'ItemID de l'élément sélectionné dans le treeview
        """
        selection = self.treeview.selection()
        # treeview.selection() retourne toujours une liste
        # on prend le 1er élément
        return int(selection[0]) if selection else None

    def populate(self, dict_decision: dict):
        """
        Vide le treeview et ajoute les lignes nécessaires
        dict_decisions correspond à un dictionnaire de décisions fourni
        par l'objet Answer
        """
        # récupération de la liste des colonnes définies pour notre treeview
        cids = self.treeview.cget('columns')
        # pour chaque décision
        for key, value in dict_decision.items():
            # récupération de son dictionnaire de méta
            dict_meta = value.dict_meta
            values = [dict_meta[cid] for cid in cids]
            self.treeview.insert("", "end", iid=str(key),
                                 text=str(key), values=values)
        # on place la sélection sur le premier élément de la liste
        # "1" car nous idenfions les décisions à partir de 1 dans Answer
        self.treeview.focus_set()
        self.treeview.selection_set("1")
        self.treeview.focus("1")


class ButtonWholeText(ttk.Button):
    """Bouton qui génère un widget Text contenant le texte d'une décision"""

    def __init__(self, parent, decision_text, id_decision,
                 number_decision, *args, **kwargs):
        
        """Méthode constructrice"""
        self.parent = parent
        self.decision_text = decision_text
        self.id_decision = id_decision
        self.number_decision = number_decision
        super().__init__(parent, *args, **kwargs)
        self.configure(
            text="Afficher le texte de la décision sélectionnée",
            command=self._on_display_text
        )

    def _on_display_text(self):
        """Affiche un widget"""
        top = tk.Toplevel(
            self.parent,
        )
        top.title(f"{self.number_decision} / {self.id_decision}")
        top.columnconfigure(0, weight=1),
        top.rowconfigure(0, weight=1)
        # Placement de la fenêtre
        place_windows(top, 600, 600, top.nametowidget("."))
        text = tk.Text(
            top,
            wrap="word"
        )
        text.grid(column=0, row=0, sticky="ewsn")
        # On ajoute le texte
        text.insert("1.0", self.decision_text)
        # ajout d'une scrollbar
        self.scrollbar = ttk.Scrollbar(
            top,
            orient=tk.VERTICAL,
            command=text.yview
        )
        text.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky=tk.W + tk.E + tk.N + tk.S)


class CustomNotebook(ttk.Notebook):
    """
    Un Notebook avec des boutons pour fermer chaque onglet
    source : https://stackoverflow.com/questions/39458337/
    is-there-a-way-to-add-close-buttons-to-tabs-in-tkinter-ttk-notebook/
    39459376#39459376
    """

    __initialized = False
    # Permet de recréer un nouveau style si le style a déjà été initialisé
    # lors d'une précédente tentative.
    # Sans cela les images pour la croix disparaissent après la 1re tentative
    _id_style_close = 1

    def __init__(self, *args, **kwargs):
        """
        Fonction d'initialisation
        """
        self.__initialize_custom_style()
        CustomNotebook.__initialized = True

        kwargs["style"] = "CustomNotebook"
        ttk.Notebook.__init__(self, *args, **kwargs)

        self._active = None

        self.bind("<ButtonPress-1>", self._on_close_press, True)
        self.bind("<ButtonRelease-1>", self._on_close_release)
        CustomNotebook._id_style_close += 1

    def _on_close_press(self, event):
        """
        Called when the button is pressed over the close button
        """

        element = self.identify(event.x, event.y)

        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            # ajout de ma part pour bloquer la suppression de l'onglet accueil
            if not index == 0:
                self.state(['pressed'])
                self._active = index
                return "break"

    def _on_close_release(self, event):
        """
        Called when the button is released
        """
        if not self.instate(['pressed']):
            return

        element = self.identify(event.x, event.y)
        if "close" not in element:
            # user moved the mouse off of the close button
            return

        index = self.index("@%d,%d" % (event.x, event.y))
        # ajout de ma part pour bloquer la suppression de l'onglet accueil
        if index == 0:
            pass
        elif self._active == index:
            self.forget(index)
            self.event_generate("<<NotebookTabClosed>>")

        self.state(["!pressed"])
        self._active = None

    def __initialize_custom_style(self):
        self._images = (
            tk.PhotoImage("img_close", data='''
                R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
                '''),
            tk.PhotoImage("img_closeactive", data='''
                R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
                AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=
                '''),
            tk.PhotoImage("img_closepressed", data='''
                R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
            ''')
        )
        style = ttk.Style()
        # Définit le nom de l'élément à créer
        element_name = "close" + str(self._id_style_close)
        # Pour l'appel de l'élément plus tard
        element_call = "CustomNotebook." + element_name
        style.element_create(element_name, "image", "img_close",
                             ("active", "pressed", "!disabled",
                              "img_closepressed"),
                             ("active", "!disabled", "img_closeactive"),
                             border=8, sticky='')
        style.layout("CustomNotebook", [("CustomNotebook.client",
                                         {"sticky": "nswe"})])
        style.layout("CustomNotebook.Tab", [
            ("CustomNotebook.tab", {
                "sticky": "nswe",
                "children": [
                    ("CustomNotebook.padding", {
                        "side": "top",
                        "sticky": "nswe",
                        "children": [
                            ("CustomNotebook.focus", {
                                "side": "top",
                                "sticky": "nswe",
                                "children": [
                                    ("CustomNotebook.label", {"side": "left",
                                                              "sticky": ''}),
                                    (element_call, {"side": "left",
                                     "sticky": ''}),
                                    ]
                            })
                        ]
                    })
                ]
            })
        ])


class NoneEmptyEntry(ttk.Entry):
    """
    Une entry qui ne doit pas être vide
    Cette classe n'est pas utilisée actuellement dans l'application
    mais pourrait l'être à l'avenir. Elle est intéressante.
    """

    def __init__(self, parent, *args, **kwargs):
        "constructeur"
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        # variable pour le message d'erreur
        self.error = tk.StringVar()
        # système de validation d'un widget
        self.configure(
            validate='focusout',
            validatecommand=(self.register(self._validate),),
            invalidcommand=(self.register(self._on_invalid),)
        )

    def _validate(self):
        "Si l'entry est vide, on retourne False"
        if not self.get():
            return False
        return True

    def _on_invalid(self):
        # On affiche un message durant un bref moment ensuite on le retire
        self.error.set("Ce champ doit être complété.")
        self.parent.after(3000, self._empty_error)

    def _empty_error(self):
        self.error.set("")


class CustomMessageBox(tk.Toplevel):
    """
    Instancie une fenêtre supérieure similaire à celle
    disponible dans tk.Messagebox mais celle-ci peut
    être placée au centre du widget root"""

    image_type = {
        "question": "::tk::icons::question",
        "warning": "::tk::icons::warning",
        "error": "::tk::icons::error",
        "information": "::tk::icons::information"
    }

    def __init__(self, title, message, type, root=None, *args, **kwargs):
        """
        Fonction d'initialisation"""
        super().__init__(*args, **kwargs)
        self.title(title)
        if not root:
            self.root = self.master
        else:
            self.root = root
        place_windows(self, 430, 100, self.root)
        # Seule cette fenêtre est accessible
        self.focus_set()
        self.grab_set()
        self.resizable(False, False)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        # Image
        ttk.Label(self, image=self.image_type[type]).grid(row=0, column=0,
                                                          pady=(7, 0),
                                                          padx=(7, 0),
                                                          sticky=tk.W)
        # Message
        # Méthode pour le wrapping trouvée ici :
        # https://stackoverflow.com/questions/11949391/
        # how-do-i-use-tkinter-to-create-line-wrapped-text-that-fills-the-width-of-the-win
        message_label = ttk.Label(self, text=message,
                                  justify=tk.LEFT)
        message_label.bind('<Configure>',
                           lambda e: message_label.config(
                                wraplength=message_label.winfo_width())) 
        message_label.grid(row=0, column=1, columnspan=2,
                           pady=(7, 4), sticky=tk.W)
        # Partie dédiée à la fermeture des fenêtre
        if type == 'question':
            buttons_frame = tk.Frame(self)
            buttons_frame.grid(row=1, column=0,
                               columnspan=2)
            buttons_frame.columnconfigure(0, weight=1)
            ttk.Button(buttons_frame, text="Oui",
                       command=self.master.destroy).grid(
                                                        row=1,
                                                        column=0,
                                                        sticky=tk.W + tk.E)
            ttk.Button(buttons_frame, text="Annuler",
                       command=self._destroy_window).grid(
                                                     row=1,
                                                     column=1,
                                                     padx=(7, 7),
                                                     sticky=tk.W + tk.E)
        else:
            self._ok_button = tk.Button(self, text="OK",
                                        command=self._destroy_window)
            self._ok_button.grid(
                                row=1,
                                column=0,
                                columnspan=2,
                                sticky=tk.E + tk.W,
                                padx=120,
                                pady=(0, 2))
            self._ok_button.focus_set()
            self._ok_button.bind('<Return>', func=self._destroy_window)

    def _destroy_window(self, event=None):
        self.destroy()


def place_windows(win_to_place: tk.Tk, width, height, root="screen"):
    """
    Positionne la fenêtre donnée au centre de la fenêtre root"""
    # Si le root est l'écran
    if root == "screen":
        screen_width = win_to_place.winfo_screenwidth()
        screen_height = win_to_place.winfo_screenheight()
        center_x = int(screen_width/2 - width / 2)
        center_y = int(screen_height/2 - height / 2)
        win_to_place.geometry(
            f'{width}x{height}' +
            f'+{center_x}+{center_y}')
    # Si le root est une autre fenêtre tkinter
    else:
        diff_x = (root._width // 2 - width // 2)
        diff_y = (root._height // 2 - height // 2)
        position_x = root.winfo_rootx() + diff_x
        position_y = root.winfo_rooty() + diff_y
        win_to_place.geometry(
            f'{width}x{height}' +
            f'+{position_x}+{position_y}')


# ===========================
# Test unitaire
if __name__ == "__main__":
    root = tk.Tk()
    root.columnconfigure(1, weight=1)
    ButtonWholeText(
        root,
        "salut, ça va\nMoi, ça va !"
    ).pack()
    root.mainloop()
