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
    url = "https://gateway.marvel.com/v1/public/comics"
    params = {
        'upc': upc,
        **get_marvel_auth()
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Marvel API error: {response.status_code}")
    
    data = response.json()
    return data["data"]["results"][0] if data else None

def get_previous_issues(comic):
    series_url = comic["series"]["resourceURI"]
    curr_issue = comic["issueNumber"]

    url = series_url + "/comics"
    params = {
        "orderBy": "issueNumber",
        "limit": 100,
        "noVariants": "true",
        **get_marvel_auth()
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Marvel API error: {response.status_code}")
    
    data = response.json()

    if data:
        data = data["data"]["results"]

        #Get the previous issues and no variants
        previous = [c for c in data if c["issueNumber"] < curr_issue]
        return previous

    return None

def main():
    upc = "75960620570700311" # Example: Aliens VS. Avengers (2024) #3
    comic = get_comic_by_upc(upc)

    if comic:
        summaries = []
        print(f'''Marvel Comics AI Recapper
    Title: {comic["title"]}
    Stories: {comic["stories"]}
    Events: {comic["events"]}''')

        previous_issues = get_previous_issues(comic)
        
        print("Previous Issue Titles")
        for c in previous_issues:
            summaries.append(c["description"])
            print(c["title"])

    else:
        print("No comic found for this UPC.")
        return


if __name__ == "__main__":
    main()