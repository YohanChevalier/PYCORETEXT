from faulthandler import disable
import tkinter as tk
from tkinter import ttk
import app_widgets_class as wc


class Test(ttk.Labelframe):
    "Frame principal qui contiendra les sous_frames de la recherche"

    def __init__(self, master, text="RECHERCHE", *args, **kwargs):
        super().__init__(master=master, text=text, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self._vars = {
            "test": tk.StringVar(),
            "test1": tk.StringVar(),
            "disable": tk.StringVar()
                    }
        self.liste = ('Argentina', 'Australia', 'Belgium', 'Brazil',
                      'Canada', 'China', 'Denmark', 'Finland', 'France',
                      'Greece', 'India')
        self.liste2 = ('Argentina', 'Australia', 'Belgium', 'Brazil',
                      'Canada', 'China', 'Denmark', 'Finland', 'France',
                      'Greece', 'India')
        self.lb = wc.LabelInput(
            self, label="Liste 1", var=self._vars["test"],
            input_class=tk.Listbox, input_args={
                            "selectmode": tk.MULTIPLE},
            disable_vars=[self._vars["test1"]]
        )
        self.lb.grid(column=0, row=0)
        # on bind l'input à une fonction de récupération des données
        self.lb.input.bind('<<ListboxSelect>>',
                           lambda event, widget=self.lb: self.update(widget))
        # On ajoute les valeurs dans la listbox
        for i in self.liste:
            self.lb.input.insert(tk.END, i)

        # # 2e liste
        self.lb1 = wc.LabelInput(
            self, label="Liste 2", var=self._vars["test1"],
            input_class=tk.Listbox, input_args={
                            "selectmode": tk.MULTIPLE},
            # disable_vars=[self._vars["test"], self._vars["disable"]]
        )
        self.lb1.grid(column=0, row=2)
        # on bind l'input à une fonction de récupération des données
        self.lb1.input.bind('<<ListboxSelect>>',
                            lambda event, widget=self.lb1: self.update(widget))
        # On ajoute les valeurs dans la listbox
        for i in self.liste2:
            self.lb1.input.insert(tk.END, i)

        wc.LabelInput(self, "Disable", var=self._vars["disable"],
                      input_class=ttk.Entry).grid(column=0, row=1)

    def update(self, widget):
        # note a is a tuple containing the line numbers of the selected
        # element counting from 0.
        selection = widget.input.curselection()
        to_return = []
        for i in selection:
            print("indice =>", i)
            item = self.lb.input.get(i, i)
            item = "".join(item)
            print("item =>", i)
            to_return.append(item)
            print(to_return)
        to_return = " ".join(to_return)
        self._vars["test"].set(to_return)
        print(self._vars["test"].get())

# def update(*args):
#     # note a is a tuple containing the line numbers of the selected
#     # element counting from 0.
#     a = lbox.curselection()
#     print( type(a), a )
#     lb_value.set( countrynames[ a[0] ] ) #Update the control variable's value.
#
# lbox.bind('<<ListboxSelect>>', update)
#
# lb_value=tk.StringVar()
# lb = tk.Label(root, textvariable=lb_value, bg='yellow')
# lb.grid(row=0, column=1)


if __name__ == "__main__":
    root = tk.Tk()
    root.columnconfigure(0, weight=1)
    Test(root, "TEST").grid(column=1, row=1)
    root.mainloop()
