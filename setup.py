import config as c
import requests
import json
import logging
from pymongo import MongoClient
from urllib.parse import quote
# from helpers.data_schema import generate_data_schema
from db.db_helpers import select_all

# updates_endpoint = f"https://api.telegram.org/bot{c.tg_credentials['token']}/getUpdates"


# def retrieve_regions_from_db():
#     client = MongoClient()
#     db = client.kplc_region_demo
#     regions = db.affected_regions
#     all_locs = list(regions.find())
#     return all_locs


all_locations = select_all("kplc_region_demo", "affected_regions")


def build_response(list_of_areas):
    msg = "<b>These areas will be affected by scheduled maintenance tomorrow</b> \n"

    for i, region in enumerate(list_of_areas):
        msg = f"{msg}\n <b>{i + 1}. {region['region']} </b>\n"

        for area in region['areas']:
            msg = f"{msg}\n <em><u>{area['area']}</u></em> \n"
            print(area['locations'])
            for location in area['locations']:
                msg = f"{msg} <pre>-{location}</pre> \n"

    print(msg)
    return msg


def get_chat_id(request):
    try:
        req_json = request.decode('utf-8')
        results = json.loads(req_json)
        chat_id = results['message']['chat']['id']

        print(chat_id)
        # results = requests.get(url).json()
        return chat_id


    except Exception as e:
        print(f'Exception: {e}')

    # print(results.json())


def get_message(request):
    try:

        req_json = request.decode('utf-8')
        results = json.loads(req_json)
        print(results['message']['text'])
        return results['message']['text']
    except Exception as e:
        print(f'Exception: {e}')


def send_message(chat_id, msg):
    send_endpoint = f"https://api.telegram.org/bot{c.tg_credentials['token']}/sendMessage"
    text = quote(msg)
    url = f"{send_endpoint}?chat_id={chat_id}&text={text}&parse_mode=html"
    response = requests.post(url)
    print(response.text)


def welcome(data):
    chat_id = get_chat_id(data)

    message = "Hi, Welcome to Kenya Power Scheduled Maintenance. " \
              "To get started reply with any of the following commands:" \
              "Type 'all' to get all the areas that will be affected."
    send_message(chat_id, message)


def handle_scenarios(data, text):
    chat_id = get_chat_id(data)

    if text == 'all':
        outgoing_message = build_response(all_locations)

    elif text == 'test':
        outgoing_message = """
            <b>bold</b>, <strong>bold</strong>
            <i>italic</i>, <em>italic</em>
            <u>underline</u>, <ins>underline</ins>
            <s>strikethrough</s>, <strike>strikethrough</strike>, <del>strikethrough</del>
            <b>bold <i>italic bold <s>italic bold strikethrough</s> <u>underline italic bold</u></i> bold</b>
            <a href="http://www.example.com/">inline URL</a>
            <a href="tg://user?id=123456789">inline mention of a user</a>
            <code>inline fixed-width code</code>
            <pre>pre-formatted fixed-width code block</pre>
            <pre><code class="language-python">pre-formatted fixed-width code block written in the Python programming language</code></pre>
            """

    elif text == 'me':
        outgoing_message = "<pre>You are the love of my life, Bridget </pre>"

    else:
        outgoing_message = "<b><em>Incorrect input. Please enter the specified commands:</em></b> <em>all</em>"

    send_message(chat_id, outgoing_message)
