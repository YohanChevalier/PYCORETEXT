"""
Test d'une fonction qui pose des tags
dans un widget text selon plusieurs arguments données
"""


import tkinter as tk
import webbrowser as web
import test_find_hyperlinks as fhyper

message = fhyper.text


def open_url(url):
    web.open_new_tab(url)


def enter(event):
    text.config(cursor="hand2")


def leave(event):
    text.config(cursor="")


def add_hypertags(i_line, i_start, i_end, url):
    # ajouter un tag (début et fin)
    text.tag_add(url, i_line + '.' + str(i_start), i_line + '.' + str(i_end))
    # Le configurer en prenant l'url pour nom de tag
    text.tag_config(url, foreground="blue", underline=True)
    # Le lier à une méthode ou fonction
    text.tag_bind(url, "<Button-1>",
                  func=lambda event, url=url: open_url(
                                            url))
    text.tag_bind(url, "<Enter>", enter)
    text.tag_bind(url, "<Leave>", leave)


root = tk.Tk()
text = tk.Text(root)
text.pack()
result_search = fhyper.find_replace_hyperlink(message)
if result_search:
    text.insert('1.0', result_search[0])
    for tag in result_search[1]:
        add_hypertags("1", tag[0], tag[1], tag[2])

# url = "https://www.google.com"
# 
# hyperlinks_dict = {
#     "hyper": "https://www.google.com"
# }
# 
# text.insert("1.0", "salut yohan")
# # ajouter un tag (début et fin)
# text.tag_add(url, "1.0", "1.5")
# # Le configurer en prenant l'url pour nom de tag
# text.tag_config(url, foreground="blue", underline=True)
# # Le lier à une méthode ou fonction
# text.tag_bind(url, "<Button-1>",
#               func=lambda event, url=url: open_url(
#                                         url))
# text.tag_bind(url, "<Enter>", enter)
# text.tag_bind(url, "<Leave>", leave)
# # Récupérer les indices de début et fin d'un tag
# for tag in text.tag_ranges(url):
#     print(str(tag))
#     print(type(str(tag)))
# # obtenir la liste des tags_name
# for name in text.tag_names():
#     print(name)
root.mainloop()

