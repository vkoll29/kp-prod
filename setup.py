import config as c
import requests
import json
import logging
from urllib.parse import quote
# from helpers.data_schema import generate_data_schema
from db.db_helpers import insert_many_items, select_all

# updates_endpoint = f"https://api.telegram.org/bot{c.tg_credentials['token']}/getUpdates"


# def retrieve_regions_from_db():
#     client = MongoClient()
#     db = client.kplc_region_demo
#     regions = db.affected_regions
#     all_locs = list(regions.find())
#     return all_locs

# locs = generate_data_schema()
# insert_many_items('kplc_region_demo', 'affected_regions', locs)


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


def get_chat_info(request):
    try:
        req_json = request.decode('utf-8')
        results = json.loads(req_json)
        chat_id = results['message']['chat']['id']
        f_name = results['message']['chat']['first_name']

        # print(chat_id)
        # results = requests.get(url).json()
        return chat_id, f_name

    except Exception as e:
        print(f'Exception: {e}')

# def get_chat_info(request):


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
    print(response)


def welcome(data):
    try:
        chat_id, f_name = get_chat_info(data)

        message = f"<pre>Hi {f_name}, Thanks for showing interest in this scheduled maintenance alert system." \
                  "The app is currently heavily in development." \
                  "However, once there is a new release (whether testing or stable) you will be the first to know. " \
                  "We promise</pre>"
        send_message(chat_id, message)
        print(chat_id)
    except Exception as e:
        print(f'Error: Not a direct chat\n Exception: {e}')


def handle_scenarios(data, text):
    chat_id, f_name = get_chat_info(data)

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

    else:
        outgoing_message = "<b><em>Incorrect input. Please enter the specified commands:</em></b> <em>all</em>"

    send_message(chat_id, outgoing_message)
