text = (
    """Article <a href="https://www.legifrance.gouv.fr\
/search/code?tab_selection=code&searchField=ALL&query=1009-1+code+de+procedure+civile&page=1&init=true"\
target="_blank">1009-1</a> du code de procedure civile, \
la radiation du pourvoi forme le 23 novembre 2021 par la societe [1] \
a l'encontre de l'arret rendu le 9 septembre 2021 par la cour d'appel de \
Versailles, dans l'instance enregistree sous le numero P 21-24.568.
Article <a href="https://www.google.fr\
/search/code?tab_selection=code&searchField=ALL&query=1009-1+code+de+procedure+civile&page=1&init=true"\
target="_blank">google</a> du code de procedure civile, \
la radiation du pourvoi forme le 23 novembre 2021 par la societe [1] \
a l'encontre de l'arret rendu le 9 septembre 2021 par la cour d'appel de \
Versailles, dans l'instance enregistree sous le numero P 21-24.568.""")

# Trouver le premier <a> dans le texte
chunked_first = text[text.find("<a"):text.find("</a")+5]
# Trouver le premier <a> dans le texte
chunked_last = text[text.rfind("<a"):text.rfind("</a")+5]
print(chunked_first)
print(chunked_last)
# Si aucun chunck trouvé (find renvoie -1):
empty_chunk = text[-1:-1]
if not empty_chunk:
    print(False)
else:
    print(True)
# Trouver l'url dans la 1re chunck
url = chunked_first[chunked_first.find("https"):chunked_first.find("target")]
print(url)
# Trouver la target dans la 1re chunck
target = chunked_first[chunked_first.find(">")+1:chunked_first.find("</a>")]
print(target)
# Trouver l'url dans la 2e chunck
url = chunked_last[chunked_last.find("https"):chunked_last.find("target")]
print(url)
# Trouver la target dans la 2e chunck
target = chunked_last[chunked_last.find(">")+1:chunked_last.find("</a>")]
print(target)


def addhyperlinks():
    """
    Boucle sur le texte :
      /1 recherche <a>...</a>
      /2 création url et target
      /3 nouvelle string
    De cette manière les occurences de <a>...</a> sont traitées une à une
    """
    while 1:
        pass