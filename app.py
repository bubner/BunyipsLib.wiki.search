import requests
from thefuzz import process
from flask import Flask, jsonify, redirect
from urllib.parse import quote

app = Flask(__name__)

ALL_WIKI_FILE_NAMES = [
    "Creating-OpModes",
    # "_Footer",
    "Home",
    "Installation",
    "IO",
    "Paradigms",
    "RoadRunner",
    "Robot-Configuration",
    "Subsystems",
    "Utilities",
    "Vision"
]

def get_direct_wiki_file_name(file_pattern) -> str | None:
    match = process.extractOne(file_pattern, ALL_WIKI_FILE_NAMES)
    return match[0] if match[1] >= 70 else None

def get_raw_wiki_file(file):
    return f"https://raw.githubusercontent.com/wiki/Murray-Bridge-Bunyips/BunyipsLib/{file}.md"

def get_wiki_page_link(name):
    return f"https://github.com/Murray-Bridge-Bunyips/BunyipsLib/wiki/{name}"
    
@app.route("/")
def index():
    return redirect(get_wiki_page_link(""))

@app.route("/<string:search>")
def search(search: str):
    if name := get_direct_wiki_file_name(search):
        # Can just return the page if we find it
        return redirect(get_wiki_page_link(name))
    # Otherwise we need to search every page for this key phrase
    results = []
    for page_name in ALL_WIKI_FILE_NAMES:
        page = requests.get(get_raw_wiki_file(page_name))
        if not page.ok:
            return jsonify({"message": f"Failed to retrieve page '{page_name}' from GitHub!", "response": page.json()}), 500
        page_data = page.text.splitlines()
        results.append(process.extractOne(search, page_data) + (page_name,)) # (string match, score, page)
    # Construct new wiki page based on the strongest one
    strongest_match = max(results, key=lambda x: x[1]) # by score
    # We now need to strip down the string match so we can put it into a link fragment
    # then we can construct a new URL to send the user to with the match. We use the URI text fragment API.
    # We also use quote from urllib to make sure input is valid for the browser and remove some pieces
    fragment = quote(strongest_match[0].replace("#", "").replace("`", "").strip())
    return redirect(get_wiki_page_link(f"{strongest_match[2]}#:~:text={fragment}"))
    