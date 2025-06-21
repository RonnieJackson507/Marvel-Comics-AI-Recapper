from flask import Flask, request, jsonify
from dotenv import load_dotenv
from ollama import Client
import tkinter as tk
import os
import re
import requests
import hashlib
import time

# Load environment variables
load_dotenv()
MARVEL_PUBLIC = os.getenv("MARVEL_PUBLIC")
MARVEL_PRIVATE = os.getenv("MARVEL_PRIVATE")

#Set up Ollama Client
client = Client(host=os.getenv("OLLAMA_LOCAL_HOST"))

app = Flask(__name__)

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
        "orderBy": "-issueNumber",
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
        return previous[:5]

    return None

def clean_response(text):
    # Remove the think block from the deepseek-r1 model
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

@app.route('/recap', methods=['POST'])
def handle_recap():
    data = request.get_json()

    upc = data.get('upc')

    if not upc:
        return jsonify({"error": "No UPC provided"})

    comic = get_comic_by_upc(upc)
    
    system_prompt = "You are a comic book assistant that helps with making recaps of new issues of comics. Do no explain the issues, but respond directly with a recap of the stories. The output should not include: Here's a recap, <title>'s recap, <Issue #>, or any language other than english. Also make the output a short 2-3 paragraph response."

    if comic:
        #Display the Header
        message = f"Here's the recap leading up to {comic["title"]}:\n\n"

        #Find the previous issues if there is any to make a new recap for the current comic        
        previous_issues = get_previous_issues(comic)
    
        #Get all the summaries from the 5 previous issues
        if previous_issues:
            user_prompt = f"Based on the previous summaries from {comic["title"]}, write a compelling recap of recent events that could appear at the beginning of the next issue. Focus on the key developments, tone, and stakes — as if you're reminding a returning reader of what they need to know before diving in. Here is the current description for the current issue to help make a recap: {comic["description"]}\nHere are the previous summaries:"
            
            #Add the summary of each previous comic into the prompt 
            for comic in previous_issues:
                user_prompt += f"Issue {comic["issueNumber"]}: {comic["description"]}\n"
        
            #Feed the prompt with the summaries into an AI model to make a recap leading up to the current issue
            conversation = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ]

            #Get the Recap from the model
            try:
                response = client.chat(model='deepseek-r1:14b', messages=conversation)

                output = clean_response(response['message']['content'])
                message += output
            except Exception:
                return jsonify({
                    "message" : "Failed to connect to Ollama. Make sure it's running."
                })

        else:
            #No previous issues to help make a recap of the events leading up to the comic
            #Display the only summary from the comic
            message += "No previous issues found for this comic.\n" #DEBUG
            message += comic["description"]

        return jsonify({
            "message": message
        })

    else:
        return jsonify({
            "message" : "No comic found for this UPC."
        })

if __name__ == "__main__":
    app.run(debug=True)