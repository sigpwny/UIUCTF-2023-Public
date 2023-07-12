import os
import pprint

import requests

WEBHOOK = os.environ['WEBHOOK']

data = {
    'content': 'bot starting...',
    'allowed_mentions': {'parse': []},
}

r = requests.post(f'{WEBHOOK}?wait=true', json=data)
pprint.pprint(r.json())
