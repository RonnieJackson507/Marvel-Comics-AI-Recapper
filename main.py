from dotenv import load_dotenv
import os
import requests
import hashlib
import time

# Load environment variables
load_dotenv()
MARVEL_PUBLIC = os.getenv("MARVEL_PUBLIC")
MARVEL_PRIVATE = os.getenv("MARVEL_PRIVATE")

def get_marvel_auth():
    ts = str(int(time.time()))
    to_hash = ts + MARVEL_PRIVATE + MARVEL_PUBLIC
    hash_md5 = hashlib.md5(to_hash.encode('utf-8')).hexdigest()
    return {
        'ts' : ts,
        'apikey': MARVEL_PUBLIC,
        'hash': hash_md5
    }

def get_comic_by_upc(upc):
    base_url = "https://gateway.marvel.com/v1/public/comics"
    params = {
        'upc': upc,
        **get_marvel_auth()
    }

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        raise Exception(f"Marvel API error: {response.status_code}")
    
    data = response.json()
    return data["data"]["results"][0] if data else None

def main():
    upc = "75960620570700311" # Example: Aliens VS. Avengers (2024) #3
    comic = get_comic_by_upc(upc)

    if comic:
        print(f'''Marvel Comics AI Recapper
    Marvel API Public Key: {MARVEL_PUBLIC}
    Marvel API Private Key: {MARVEL_PRIVATE}
    Title: {comic["title"]}
    Description: {comic["description"]}
    Stories: {comic["stories"]}
    Events: {comic["events"]}''')
    else:
        print("No comic found for this UPC.")


if __name__ == "__main__":
    main()