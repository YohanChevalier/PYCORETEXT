import timeit
from pycoretext.api_controller import api_connexion as co
from pycoretext.api_controller import api_url

start = timeit.default_timer()

co_yohan = co.Connexion()

# ############# 0- Answer #######################################
url0_answer = api_url.UrlExport(integral=False)
url0_answer.set_criteria("chamber=", "comm")
url0_answer.set_criteria("date_start=", "2022-03-01")
url0_answer.set_criteria("date_end=", "2022-09-01")
url0_answer.set_criteria("date_type=", "creation")
url0_answer.set_criteria("jurisdiction=", "cc")

url0_1_answer = api_url.UrlSearch("boulangerie", integral=False)
url0_1_answer.set_criteria('type=', "arret")
url0_1_answer.set_criteria('publication=', "b")

# co_yohan.send_request(url0_1_answer)
# print(co_yohan.dict_answers[1].total_decisions)

# ############# 1- EXPORT #######################################
url1_export = api_url.UrlExport()
# url1_export.set_criteria("chamber=", "comm")
url1_export.set_criteria("date_start=", "2022-10-15")
url1_export.set_criteria("date_end=", "2022-10-31")
url1_export.set_criteria("date_type=", "creation")
# url1_export.set_criteria("jurisdiction=", "cc")

url1_1_export = api_url.UrlExport()
url1_1_export.set_criteria("location=", "ca_agen")
url1_1_export.set_criteria("jurisdiction=", "ca")


# co_yohan.send_request(url1_export)
# co_yohan.send_request(url1_1_export)
# print(co_yohan.dict_answers[1].total_decisions)
# for decision in co_yohan.dict_answers[1].dict_decisions.keys():
#     print("n°", decision, "id = ",
#           co_yohan.dict_answers[1].dict_decisions[decision].dict_meta["visa"])

# for key, value in co_yohan.dict_answers[1].dict_decisions[1].\
#                                             dict_meta.items():
#     print(key, "===> ", value)


# ############# 2- SEARCH #######################################
url2_search = api_url.UrlSearch("test")
# url2_search.set_criteria('location=', "ca_aix_provence")
# url2_search.set_criteria('jurisdiction=', "ca")
# url2_search.set_criteria('date_start=', "2022-10-10")
# url2_search.set_criteria('date_end=', "2022-10-11")

co_yohan.send_request(url2_search)
print(co_yohan.dict_answers[1].dict_decisions[1].dict_meta)
# print(co_yohan.dict_answers[1].wrong_response_list)
# for decision in co_yohan.dict_answers[1].dict_decisions.keys():
#     print("n°", decision, "id = ",
#           co_yohan.dict_answers[1].dict_decisions[decision].dict_meta["id"])

# ############# 3- DECISION #######################################
url3_decision = api_url.UrlDecision("6079a89f9ba5988459c4e457")
# co_yohan.send_request(url3_decision)
# print(co_yohan.dict_answers[1].decision.themes)

# ############# 4- TAXONOMY #######################################
url4_taxo = api_url.UrlTaxonomy()
url4_taxo.set_criteria("id=", "chamber")
url4_1_taxo = api_url.UrlTaxonomy()
url4_1_taxo.set_criteria('id=', "location")
url4_1_taxo.set_criteria('context_value=', "ca")

# url4_1_taxo.set_criteria('context_value=', "cc")
# co_yohan.send_request(url4_taxo)
# co_yohan.send_request(url4_1_taxo)
# print(co_yohan.dict_answers[1].__dict__)
# print(co_yohan.dict_answers[1].dict_results)
# print("context = ", co_yohan.dict_answers[2].context_value)

# Obtenir toutes les possibilités pour ca et cc
# main_list = co_yohan.dict_answers[1].list_results
# for e in main_list:
#     print(f"***{e}***")
#     url1 = api_url.UrlTaxonomy()
#     url2 = api_url.UrlTaxonomy()
#     url1.set_criteria("id=", e)
#     url1.set_criteria("context_value=", "cc")
#     url2.set_criteria("id=", e)
#     url2.set_criteria("context_value=", "ca")
#     print(url1.get_final_url(), url2.get_final_url())
#     try:
#         co_yohan.send_request(url1, internal=True)
#     except Exception as i:
#         print(i)
#     else:
#         print("--cc--")
#         print(co_yohan.dict_answers["internal"].dict_from_response)
#     try:
#         co_yohan.send_request(url2, internal=True)
#     except Exception as i:
#         print(i)
#     else:
#         print("--ca--")
#         print(co_yohan.dict_answers["internal"].dict_from_response["result"])

# ############# 5- HealthCheck #######################################
url5_health = api_url.UrlHealthCheck()
# co_yohan.send_request(url5_health, internal=False)
# print(co_yohan.dict_answers.keys())
# print(co_yohan.nb_answers)
# print(co_yohan.dict_answers[1].status)

# ############# 6- STATS #######################################
url6_stats = api_url.UrlStats()
# co_yohan.send_request(url6_stats)
# dictionnaire = co_yohan.dict_answers[1]
# for item in dictionnaire.__dict__.keys():
#     print(item, ' = ', dictionnaire.__dict__[item])

# ############# 7- requêtes multiples #######################################
# co_yohan.send_request(url1_export)
# co_yohan.send_request(url2_search)
# co_yohan.send_request(url3_decision)
# co_yohan.send_request(url4_taxo)
# co_yohan.send_request(url4_1_taxo)
# co_yohan.send_request(url5_health)
# co_yohan.send_request(url6_stats)
# print(co_yohan.dict_answers.keys())

stop = timeit.default_timer()
print('Time: ', stop - start)
