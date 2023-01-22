import asyncio
import time
import aiohttp

# Problème car le nb varie...

count = 0

async def download_site(session, url):
    global count
    async with session.get(url, headers={"accept": "application/json", 'KeyId': 'XXXX'}) as response:
        dict = await response.json()
        for item in dict['results']:
            count += 1
            print('#', count, item['id'])
#         print("Read {0} from {1}".format(response.content_length, url))



async def download_all_sites(sites):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in sites:
            task = asyncio.ensure_future(download_site(session, url))
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    sites = ['https://sandbox-api.piste.gouv.fr/cassation/judilibre/v1.0/search?page=0&query=brevet&type=arret&chamber=comm&chamber=soc',
             'https://sandbox-api.piste.gouv.fr/cassation/judilibre/v1.0/search?page=1&query=brevet&type=arret&chamber=comm&chamber=soc'] * 500 
    print(len(sites))
    start_time = time.time()
    asyncio.run(download_all_sites(sites))
    duration = time.time() - start_time
    print(f"Downloaded {len(sites)} sites in {duration} seconds")
