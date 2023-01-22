# %%
from asyncio import as_completed
import requests
from concurrent.futures import ThreadPoolExecutor as TPE, as_completed
from multiprocessing import cpu_count
# pip install ratelimit backoff
from ratelimit import limits, RateLimitException
from backoff import on_exception, expo
from time import sleep
from random import random

# décorateur: fonction qui retourne une fonction qui elle même ajoute 
# un comportement à une fonction en paramètre
def delayed(f):
    def wrapper(*a, **kwd):
        delay = a[2] if len(a) > 2 else 0
        sleep(delay)
        return f(*a, **kwd)
    return wrapper


URL = "https://sandbox-api.piste.gouv.fr/cassation/judilibre/v1.0/"
batch = 0
url_end_point = (f"export?batch={batch}&type=arret&date_start=2000-10-15&"
                 "date_end=2022-10-20&date_type=creation")

ERRORS = (
    AttributeError,
    requests.ConnectionError,
    requests.HTTPError,
    ValueError)


class GorestClient:
    def __init__(self):
        self.__session = requests.Session()

    def __call(self, method, endpoint, data={}, headers={}, files={}):
        response = {"valid": True}
        url = f"{URL}{endpoint}"
        print(url)
        try:
            # call_fn = getattr(requests, method.lower())
            # r = call_fn(url, data=data, headers=headers, files=files)
            r = self.__session.send(
                requests.Request(
                 method, url, data=data, headers=headers, files=files).prepare()
                                )
            print("test ==>", r.json())
            # tester le code de retour
            if 200 <= r.status_code < 300:
                # formater le corps de la réponse en fonction des entêtes de réponse
                if "json" in r.headers["content-type"]:
                    response["data"] = r.json()
                elif "text/" in r.headers["content-type"]:
                    response["data"] = r.text.decode(r.encoding)
                else:
                    response["data"] = r.content
            else:
                raise ValueError(
                    f"Wrong status: {r.status_code}: {r.json()['message']}")
        except ERRORS as e:
            response["valid"] = False
            response["data"] = e
        print(response)
        return response

    # décorateurs qui doivent limiter le nb d'appels par seconde
    # et gérer des exceptions permettant de recommencer quand le temps 
    # le permet
    # @limits(calls=10, period=2)
    # @on_exception(expo, RateLimitException, max_tries=5)
    # get_users = delayed(get_users)
    @delayed
    def get_users(self, batch, *a):
        try:
            print(f"page {batch} fetched")
            return self.__call(
                "GET",
                (f"export?batch={batch}&type=arret&date_start=2000-10-15&"
                 "date_end=2022-10-20&date_type=creation")
            )
        except RateLimitException as e:
            return {"valid": False, "data": e}

    def get_users_pages(self, batch_start, batch_end):
        ret = {"data": [], "errors": []}
        with TPE(max_workers=cpu_count() - 2) as pool:
            futures = [
                pool.submit(self.get_users, p, random()) for p in range(
                                            batch_start, batch_end + 1)
            ]
            for f in as_completed(futures):
                data = f.result()
                print(data)
              
            return ret


if __name__ == "__main__":
    api = GorestClient()
    data = api.get_users_pages(1, 5)