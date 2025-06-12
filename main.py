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
    series_uri = comic["series"]["resourceURI"]
    curr_issue = comic["issueNumber"]

    url = series_uri + "/comics"
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

        #Return the previous issues from newest to oldest
        previous = [comic for comic in data if comic["issueNumber"] < curr_issue]
        return previous[::-1]

    return None

def main():
    #TODO: Get the upc from the comic'c barcode
    upc = "75960620289803011"
    comic = get_comic_by_upc(upc)

    if comic:
        summaries = []
        summaries.append(comic["description"]) # Rough summary from the previous issue

        #Display current comic
        print("Marvel Comics AI Recapper")
        print(f"Current Title: {comic["title"]}")
        
        #Display the previous issues and append the summaries
        previous_issues = get_previous_issues(comic)

        if previous_issues:
            print("Previous Issue Titles:")
            for comic in previous_issues:
                summaries.append(comic["description"])
                print(comic["title"])
        else:
            print("No previous issues found for this comic.")

        #Display the summaries
        for summary in summaries:
            print(summary)
            print("-----------------------------------------------------------------------------------------------------------------------------")

    else:
        print("No comic found for this UPC.")
        return


if __name__ == "__main__":
    main()