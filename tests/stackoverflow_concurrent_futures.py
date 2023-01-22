from concurrent.futures import ThreadPoolExecutor
from requests import get as re_get


def main_function(global_page_number, headers, url_request):
    # create a list of pages number
    pages_numbers_list = [i for i in range(global_page_number)]
    # for each page, call the page_handler (MultiThreading)
    with ThreadPoolExecutor(max_workers=10) as executor:
        for item in pages_numbers_list:
            executor.submit(
                page_handler,
                item,
                url_request,
                headers
            )


def page_handler(page_number, url_request, headers):
    # we change the page number in the url request
    url_request = change_page(url_request, page_number)
    # new request with the new url
    result = re_get(url_request, headers=headers)
    result = result.json()
    # in the result, with found the list of dict in order to create the
    # final object
    final_object_creation(result['results_list'])


def change_page(url_request, new_page_number):
    "to increment the value of the 'page=' attribute in the url"
    current_nb_page = ''
    start_nb = url_request.find("page=") + len('page=')
    while 1:
        if url_request[start_nb].isdigit():
            current_nb_page = url_request[start_nb]
        else:
            break
        new_url_request = url_request.replace("page=" + current_nb_page,
                                              "page=" + str(new_page_number))
        return new_url_request        


def final_object_creation(results_list):
    'thanks to the object from requests.get(), it builts the final object'
    global current_id_decision, dict_decisions
    # each item in the results lis should be an instance of the final object
    for item in results_list:
        # On définit l'identifiant du nouvel objet Decision
        current_id_decision += 1
        new_id = current_id_decision
        # On crée l'objet Décision et on l'ajoute au dico des décisions
        dict_decisions[new_id] = FinalObject(item)


class FinalObject:
    def __init__(self, content):
        self.content = content


current_id_decision = 0
dict_decisions = {}
main_function(1000, "headers", "https://api/v1.0/search?page=0&query=test")