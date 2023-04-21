"""
Test qui doit permettre de créer une fonction pour :
1/ trouver les liens hypertextes dans un texte
2/ ne laisser que le texte d'affichage (target)
3/ Conserver et retourner les indices de ces targets avec l'url
"""


# https://stackoverflow.com/questions/27760561/tkinter-and-hyperlinks/27762692#27762692
# https://stackoverflow.com/questions/50327234/adding-link-to-text-in-text-widget-in-tkinter/50328110#50328110
# https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/text-methods.html

text = (
    """Article <a href="https://www.legifrance.gouv.fr\
/search/code?tab_selection=code&searchField=ALL&query=1009-1+code+de+procedure+civile&page=1&init=true"\
target="_blank">1009-1</a> du code de procedure civile, \
la radiation du pourvoi forme le 23 novembre 2021 par la societe [1] \
a l'encontre de l'arret rendu le 9 septembre 2021 par la cour d'appel de \
Versailles, dans l'instance enregistree sous le numero P 21-24.568.\
Article <a href="https://www.google.fr\
target="_blank">google</a> du code de procedure civile, \
la radiation du pourvoi forme le 23 novembre 2021 par la societe [1] \
a l'encontre de l'arret rendu le 9 septembre 2021 par la cour d'appel de \
Versailles, dans l'instance enregistree sous le numero P 21-24.568.""")

# # Trouver le premier <a> dans le texte
# chunked_first = text[text.find("<a"):text.find("</a")+5]
# # Trouver le dernier <a> dans le texte
# chunked_last = text[text.rfind("<a"):text.rfind("</a")+5]
# print(chunked_first)
# print(chunked_last)
# # Si aucun chunck trouvé (find renvoie -1):
# empty_chunk = text[-1:-1]
# if not empty_chunk:
#     print(False)
# else:
#     print(True)
# # Trouver l'url dans la 1re chunck
# url = chunked_first[chunked_first.find("https"):chunked_first.find("target")]
# print(url)
# # Trouver la target dans la 1re chunck
# target = chunked_first[chunked_first.find(">")+1:chunked_first.find("</a>")]
# print(target)
# # Trouver l'url dans la 2e chunck
# url = chunked_last[chunked_last.find("https"):chunked_last.find("target")]
# print(url)
# # Trouver la target dans la 2e chunck
# target = chunked_last[chunked_last.find(">")+1:chunked_last.find("</a>")]
# print(target)


def find_replace_hyperlink(text):
    """
    Trouver les balises <a></a> qui contiennent les attributs href et target
    Pour chaque occurence:
      /1 remplace <a></a> par la target (texte d'affichage)
      /2 conserve les indices de début et fin de la target dans le nouveau texte
    Retourne un tuple composé du nouveau text, et d'une liste de tuples :
        -> Chaque tuple contient l'indice de début et de fin de la target ainsi que l'URL
    Si aucune balise <a></a> alors retourne None
    """
    is_there_hyperlink = False
    indices_and_url = []
    while 1:
        # Trouver le premier <a> dans le texte
        indice_start = text.find("<a")
        if indice_start == -1:
            break
        else:
            is_there_hyperlink = True
            indice_end = text.find("</a")
            hyper = text[indice_start:indice_end+4]
            url = hyper[hyper.find("https"):hyper.find("target")]
            target = hyper[hyper.find(">")+1:hyper.find("</a>")]
            text = text[:indice_start] + target + text[indice_end + 4:]
            i_start_targed_in_new_text = indice_start
            i_end_target_in_new_text = indice_start + len(target)
            indices_and_url.append((i_start_targed_in_new_text,
                                    i_end_target_in_new_text,
                                    url))
    if is_there_hyperlink:
        return (text, indices_and_url)
    else:
        return None


result = find_replace_hyperlink(text)
if result:
    print(3 * "#", "RESULT", 3 * "#")
    print(result[0])
    print(3 * "#", "TARGETS", 3 * "#")
    for tag in result[1]:
        print(tag[2])
        print(result[0][tag[0]:tag[1]])
else:
    print("no hyperlink")
