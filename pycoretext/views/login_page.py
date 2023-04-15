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
Module contenant la classe dédiée à la page de login.
"""

import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage, ttk
from tkinter.scrolledtext import ScrolledText
from pathlib import Path
import sys


class LoginPage(tk.Toplevel):
    """
    Class définissant la fenêtre de login. Dérivée de tkinter.Toplevel
    """

    def __init__(self, *args, **kwargs):
        """
        Fonction d'initialisation
        """
        # chemins d'accès pour l'image et le texte
        # il change selon si nous sommes dans un fichier frozen (exécutable)
        # ou dans la structure normale du projet
        if getattr(sys, 'frozen', False):
            self._c_dir = Path(sys.executable).parent
        else:
            self._c_dir = Path(__file__).parent
        # dictionnaire de toutes les variables importantes
        self.var = {
            "environment": tk.StringVar(),
            "key": tk.StringVar(),
            "error_message": tk.StringVar(),
                    }
        # tracer la variable de message d'erreur
        self.var["error_message"].trace_add("write", self._on_error)
        super().__init__(*args, **kwargs)
        # récupération de l'image principale
        self._image = PhotoImage(file=self._c_dir / "image_login.png")
        # paramétrage de la fenêtre de login
        self.resizable(False, False)
        self.title("PYCORETEXT")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        # placement de la login page au centre de l'écran
        self._login_width = 500
        self._login_height = 500
        self._screen_width = self.winfo_screenwidth()
        self._screen_height = self.winfo_screenheight()
        self._center_x = int(self._screen_width/2 - self._login_width / 2)
        self._center_y = int(self._screen_height/2 - self._login_height / 2)
        self.geometry(
            f'{self._login_width}x{self._login_height}' +
            f'+{self._center_x}+{self._center_y}')

        # MAIN FRAME
        main_frame = ttk.Frame(self)
        main_frame.grid(column=0, row=0, sticky=(
            tk.W + tk.E + tk.N + tk.S), padx=40)
        main_frame.columnconfigure(0, weight=1)
        # IMAGE PRINCIPALE
        image_frame = ttk.Frame(main_frame)
        image_frame.grid(column=0, row=0, sticky=(tk.E + tk.W), pady=(4,))
        ttk.Label(image_frame, image=self._image).pack()
        # ENVIRONNEMENT
        radio_frame = ttk.Labelframe(
                            main_frame, text="Sélectionnez l'environnement :"
                                    )
        radio_frame.grid(column=0, row=2, sticky=(tk.W + tk.E), pady=(4,))
        radio_frame.columnconfigure(0, weight=1)
        for choice in ["Sandbox", "Production"]:
            ttk.Radiobutton(
                radio_frame, value=choice.lower(), text=choice,
                variable=self.var['environment']).pack(
                    side=tk.LEFT, expand=True)
        self.var["environment"].set("sandbox")  # valeur par défaut
        # CLE D'AUTHENTIFICATION API
        cle_frame = ttk.Labelframe(main_frame, text="Clé d'authentification :")
        cle_frame.grid(column=0, row=3, sticky=(tk.W + tk.E), pady=(4,))
        cle_frame.columnconfigure(0, weight=1)
        # utilisation de l'argument show pour masquer la clé
        self._key_field = ttk.Entry(cle_frame,
                                    textvariable=self.var["key"],
                                    show="*")
        self._key_field.grid(sticky=(tk.W + tk.E))
        # Traceur sur ce widget qui appelle _on_key_change à chaque modif.
        self.var['key'].trace_add('write', self._on_key_change)
        # La touche Entrée déclenchera une tentative de connexion aussi
        self._key_field.bind("<Return>", self._on_connexion)
        # CONNEXION
        self._co = ttk.Button(main_frame, text="CONNEXION", state=tk.DISABLED)
        self._co.grid(column=0, row=4, sticky=(tk.W + tk.E), pady=(4,))
        self._co.configure(command=self._on_connexion)
        # MESSAGE D'ERREUR
        mess_frame = ttk.LabelFrame(
                        main_frame,
                        text="Détails en cas d'erreur de connexion :")
        mess_frame.grid(column=0, row=5, sticky=(tk.W + tk.E))
        mess_frame.columnconfigure(0, weight=1)
        self._error_mess = ttk.Label(mess_frame)
        self._error_mess.grid(sticky=(tk.E + tk.W))
        # AVERTISSEMENT
        oridata_frame = tk.LabelFrame(main_frame, text="Avertissement")
        oridata_frame.grid(column=0, row=6, sticky=(tk.W + tk.E), pady=8)
        oridata_frame.columnconfigure(0, weight=1)
        # Widget spécial Text + Scrollbar
        self._oridata = ScrolledText(
            oridata_frame, height=8, width=50,
            font="tkDefaultFont, 7",
            wrap="word"
            )
        self._oridata.grid(sticky=(tk.W + tk.E), pady=8)
        # Permet de compléter avec un texte externe
        self._fill_oridata()
        # Permet de bloquer l'écriture pour les utilisateurs
        self._oridata.configure(state=tk.DISABLED)

    def _fill_oridata(self):
        """
        Récupère un fichier externe pour compléter oridata
        """
        with open(self._c_dir / "origine_donnees.txt", "r",
                  encoding="UTF-8") as f:
            text = f.readlines()
            count = 1
            for line in text:
                self._oridata.insert(f"{count}.0", line)
                count += 1

    def _on_key_change(self, *args, **kwargs):
        """
        Traceur sur key => si complété alors bouton de connexion actif
        """
        if self.var['key'].get():
            self._co.configure(state=tk.NORMAL)
        else:
            self._co.configure(state=tk.DISABLED)

    def _on_error(self, *args, **kwargs):
        """
        Traceur sur error_message => affiche l'erreur dans self._error_mess
        """
        if self.var["error_message"]:
            self._error_mess.configure(
                text=self.var["error_message"].get(),
                foreground="red"
                )

    def _on_connexion(self, *_):
        """
        Déclenche un évènement qui sera géré par l'application
        """
        self.event_generate('<<Connexion>>')

    def _on_closing(self):
        """
        Action réalisée lors du clic sur la croix en haut à droite de l'app"""
        if messagebox.askokcancel("Quitter",
                                  "Voulez-vous fermer l'application ?"):
            self.destroy()
