import requests
import json
import os
import sqlite3
import time
from urllib3.exceptions import InsecureRequestWarning

con = sqlite3.connect(":memory:")
cur = con.cursor()
# Ignoring warnings for local certs. Remove this if using external secure connection, instead of cluster internal one
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


SLACK_NOTIFY_URL = os.getenv('SLACK_NOTIFY_URL')
RANCHER_URL = os.getenv('RANCHER_URL')
RANCHER_TOKEN = os.getenv('RANCHER_TOKEN')

headersList = {
 "Accept": "application/json",
 "Content-Type": "application/json",
 "Authorization": f"Bearer {RANCHER_TOKEN}",
}
payload = ""


def check_rancher_status():
    try:
        # Ignoring warnings for local certs. Remove verify=False if using external secure connection, instead of cluster internal one
        request_response = requests.request("GET", RANCHER_URL, data=payload,  headers=headersList, verify=False)
    except requests.exceptions.ConnectionError as e:
        raise SystemExit(f'FATAL ERROR: {e}\n   Cannot connect to rancher URL')
    try:
        data = json.loads(request_response._content)
    except json.decoder.JSONDecodeError as e:
        raise SystemExit(f'FATAL ERROR: {e}\n  Rancher api data cannot be parsed, check url')
    try:
        for i in data["data"]:
            for j in i['status']['conditions']:
                if "Ready" in j['type']:
                    check_exists = 0
                    cluster_name = i['metadata']['labels']['management.cattle.io/cluster-display-name']
                    cluster_status = j['status']
                    cur.execute("SELECT count(*) FROM clusters WHERE name = ?", (cluster_name, ))
                    check_exists = cur.fetchone()[0]
                    if check_exists == 0:
                        cur.execute("INSERT INTO clusters VALUES (?, ?, ?)", (cluster_name, cluster_status, ''))
                    else:
                        cur.execute("UPDATE clusters SET ready = ? where name = ?", (cluster_status, cluster_name))
    except KeyError as e:
        raise SystemExit(f'FATAL ERROR: {e}\n  Rancher api data cannot be parsed, check token')


def send_notif_text(data):
    slack_data = {'text': data}
    try:
        _ = requests.post(
            SLACK_NOTIFY_URL, data=json.dumps(slack_data),
            headers={'Content-Type': 'application/json'}
        )
    except requests.exceptions as e:
        raise SystemError(f'ERROR: {e}\n   Cannot send notification')


def setup_db():
    cur.execute('''CREATE TABLE clusters
                (name text PRIMARY KEY, ready text, notif text)''')
    con.commit()


def check_updates():
    cur.execute('SELECT name, ready, notif FROM clusters')
    for row in cur.fetchall():
        if "True" not in row[1]:
            if "sync" not in row[2]:
                notif_string = f":rotating_light: Cluster {row[0]} is not ready, or not in sync with Fleet, please check from Rancher :warning:"
                send_notif_text(notif_string)
                cur.execute('UPDATE clusters SET notif = ? where name = ?', (f'{notif_string}', f'{row[0]}'))
                con.commit()
        else:
            cur.execute('UPDATE clusters SET notif = ? where name = ?', ('', f'{row[0]}'))
            if "rotating_light" in row[2]:
                notif_string = f"Cluster {row[0]} is in sync. :white_check_mark:"
                send_notif_text(notif_string)
                cur.execute('UPDATE clusters SET notif = ? where name = ?', (f'{notif_string}', f'{row[0]}'))
                con.commit()


if __name__ == "__main__":
    setup_db()
    while True:
        check_rancher_status()
        check_updates()
        time.sleep(60)
