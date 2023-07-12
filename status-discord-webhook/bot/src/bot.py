import datetime
import enum
import json
import os
import time

import requests

from kube import K8sClient

if os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount'):
    client = K8sClient.from_serviceaccount()
else:
    client = K8sClient.from_file()

WEBHOOK = os.environ['WEBHOOK']
MESSAGE_ID = os.environ['MESSAGE_ID']


class Status(enum.Enum):
    NO_HEALTHCHECK = enum.auto()
    UNHEALTHY = enum.auto()
    HEALTHY = enum.auto()
    UPDATING = enum.auto()
    DOWN = enum.auto()

    @property
    def is_okay(self):
        return self is self.HEALTHY or self is self.NO_HEALTHCHECK


print('running...')
r = requests.patch(f'{WEBHOOK}/messages/{MESSAGE_ID}',
                   json={'content': 'bot starting...'})
print(r.content)

while True:
    challenges = client.get_objects('challenges')

    challenges = [
        chal for chal in challenges
        if chal['spec']['deployed']
        # Commented due to custom ingresses
        # and chal['spec']['network']['public']

        # Set to non-empty-string to hide
        and not chal['metadata'].get(
            'annotations', {}).get('uiuc.tf/hidden-from-status')
    ]

    statuses = {}
    for chal in challenges:
        name = chal['metadata']['name']
        deployments = client.get_objects('deployments', f'app={name}')
        if len(deployments) != 1:
            # Badly coded challenge.yaml
            statuses[name] = Status.DOWN
            continue

        deployment, = deployments

        all_replicas = deployment['status'].get('replicas', 0)
        if not all_replicas:
            statuses[name] = Status.DOWN
            continue

        if deployment['status'].get('updatedReplicas', 0) != all_replicas:
            # Consider chals in the middle of a rolling update unhealthy
            # since the update may have failed and the rolling update stalls
            statuses[name] = Status.UPDATING
            continue

        if deployment['status'].get('readyReplicas', 0) != all_replicas:
            # healthcheck fail and pod is being restarted
            statuses[name] = Status.UNHEALTHY
            continue

        # Should be healthy, check of existance of healthcheck pod
        if len(deployment['spec']['template']['spec']['containers']) > 1:
            statuses[name] = Status.HEALTHY
        else:
            statuses[name] = Status.NO_HEALTHCHECK

    challenges.sort(key=lambda chal: (
        statuses[chal['metadata']['name']] != Status.HEALTHY,
        chal['metadata']['name']))

    color = 0x00ff00 if all(statuses[chal['metadata']['name']].is_okay
                            for chal in challenges) else 0xffff00

    message = {
        'content': '',
        'embeds': []
    }

    # hopefully we dont go over the max embed count, whatever that is
    MAX_FIELDS_IN_EMBED = 18
    embed_groups = [challenges[i:i+MAX_FIELDS_IN_EMBED]
                    for i in range(0, len(challenges), 18)]

    NUM_PER_ROW = 3

    for embed_group in embed_groups:
        NUM_ROWS = (NUM_PER_ROW + len(embed_group) - 1) // NUM_PER_ROW
        embed = {
            'color': color,
            'fields': [],
            'footer': {'text': 'Last Updated'},
            'timestamp': datetime.datetime.now().isoformat()+'Z'
        }
        for i in range(NUM_ROWS):
            for j in range(NUM_PER_ROW):
                idx = i * NUM_PER_ROW + j
                field = {
                    'name': '\u200b',
                    'value': '\u200b',
                    'inline': True
                }
                if idx < len(embed_group):
                    chal = embed_group[idx]
                    name = chal['metadata']['name']
                    status = statuses[name]

                    rcolor = {
                        Status.NO_HEALTHCHECK: ':yellow_circle:',
                        Status.UNHEALTHY: ':red_circle:',
                        Status.HEALTHY: ':green_circle:',
                        Status.UPDATING: ':blue_circle:',
                        Status.DOWN: ':black_circle:',
                    }[status]

                    healthmsg = {
                        Status.NO_HEALTHCHECK: 'unknown',
                        Status.UNHEALTHY: 'unhealthy',
                        Status.HEALTHY: 'healthy',
                        Status.UPDATING: 'updating',
                        Status.DOWN: 'down',
                    }[status]

                    # rename disabled -> unknown, more self explanatory
                    field = {
                        'name': f'{rcolor} {name}',
                        'value': healthmsg,
                        'inline': True
                    }
                embed['fields'].append(field)
            if i != NUM_ROWS-1:
                embed['fields'].append(
                    {'name': '\u200b', 'value': '\u200b', 'inline': False})
        message['embeds'].append(embed)

    print(json.dumps(message))
    r = requests.patch(f'{WEBHOOK}/messages/{MESSAGE_ID}', json=message)
    print(r.status_code, r.content)

    time.sleep(10)
