import tkinter as tk
from tkinter import ttk


class ProgressWindow(tk.Toplevel):
    "class affichant une fenêtre durant les chargements"

    def __init__(self, *args, **kwargs):
        """Fonction initialisatrice"""
        super().__init__(*args, **kwargs)
        self.geometry("+300+100")
        self.resizable(True, False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame = ttk.Frame(
            self,
        )
        main_frame.grid(column=0, row=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        ttk.Label(
            main_frame,
            text="Veuillez patienter"
        ).grid(column=0, row=0, sticky=tk.W)
        progress = ttk.Progressbar(
            main_frame,
            orient="horizontal",
            length=100,
            maximum=50,
            value=25,
            mode='indeterminate')
        progress.grid(sticky=tk.W + tk.E)
        progress.start(10)


if __name__ == "__main__":
    root = tk.Tk()

    def start_progress():
        ProgressWindow(root)

    ttk.Button(
        root,
        text="Start",
        command=start_progress
    ).pack()

    root.mainloop()
