#-*- coding: utf-8 -*-
# Python version 3.4
# The use of the ttk module is optional, you can use regular tkinter widgets

from tkinter import *
from tkinter import ttk

main = Tk()
main.title("Multiple Choice Listbox")
main.geometry("+50+150")
frame = ttk.Frame(main, padding=(3, 3, 12, 12))
frame.grid(column=0, row=0, sticky=(N, S, E, W))

valores = StringVar()
valores.set("Carro Coche Moto Bici Triciclo Patineta Patin Patines Lancha Patrullas")

lstbox = Listbox(frame, listvariable=valores, selectmode=MULTIPLE, width=20, height=10)
lstbox.grid(column=0, row=0, columnspan=2)

def select():
    reslist = list()
    seleccion = lstbox.curselection()
    for i in seleccion:
        entrada = lstbox.get(i)
        reslist.append(entrada)
    for val in reslist:
        print(val)

btn = ttk.Button(frame, text="Choices", command=select)
btn.grid(column=1, row=1)

main.mainloop()