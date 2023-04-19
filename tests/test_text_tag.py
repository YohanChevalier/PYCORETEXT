import tkinter as tk
import webbrowser as web


def open_url(url):
    web.open_new(url)


root = tk.Tk()
text = tk.Text(root)
text.pack()

hyperlinks_dict = {
    "hyper": "https://www.google.com"
}

text.insert("1.0", "salut yohan")
# ajouter un tag (début et fin)
text.tag_add("hyper", "1.0", "1.5")
# Le configurer
text.tag_config("hyper", foreground="blue", underline=True)
# Le lier à une méthode ou fonction
text.tag_bind("hyper", "<Button-1>",
              func=lambda event, url="hyper": open_url(
                                        hyperlinks_dict["hyper"]))
# Récupérer les indices de début et fin d'un tag
for tag in text.tag_ranges("hyper"):
    print(str(tag))
    print(type(str(tag)))
# obtenir la liste des tags_name
for name in text.tag_names():
    print(name)
root.mainloop()
