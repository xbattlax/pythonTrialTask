import os

from flask import request, Flask, send_from_directory, after_this_request
from azure.cognitiveservices.search.websearch import WebSearchClient
from azure.cognitiveservices.search.websearch.models import SafeSearch
from msrest.authentication import CognitiveServicesCredentials
import requests
import json

subscription_key = "02ba10ef4ae441a3b0ea2a3d1e2aaeba"
search_url = "https://api.bing.microsoft.com/v7.0/search"

app = Flask(__name__)


def query(q, offset):
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    params = {"q": q, "textDecorations": True, "textFormat": "HTML", "count": 50, "offset": offset}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    return json.loads(response.content)["webPages"]["value"]


def get100Result(q):
    data = query(q, 0)
    if data:
        data.extend(query(q, 50))
        return data


def sort_by_key(list):
    return list['name']


def sortJson(list):
    return sorted(list, key=sort_by_key)


@app.route('/search/<string:q>', methods=['GET'])
def getJson(q):
    dataF = get100Result(q)
    with open('json_data.json', 'w') as outfile:
        json.dump(sortJson(dataF), outfile)
    @after_this_request
    def remove_file(response):
        try:
            os.remove('json_data.json')
        except Exception as error:
            app.logger.error("Error removing", error)
        return response
    return send_from_directory(".",
                               "json_data.json", as_attachment=True)


