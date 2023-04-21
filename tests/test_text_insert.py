import tkinter as tk

l = [
    "salut\n\n",
    "hello",
    "youpi",
    "yohan",
    "saperlipopette\n",
    "guiseslo"
]

root = tk. Tk()
text = tk.Text(root)
text.pack()
for item in l:
    text.insert(tk.END, item)
# last line
print(text.index('end - 1 chars'))
root.mainloop()
