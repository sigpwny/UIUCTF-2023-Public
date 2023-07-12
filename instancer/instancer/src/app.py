# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import secrets

import yaml
import requests

from flask import Flask, abort, redirect, render_template, request
from kube import K8sClient

ACCEPTED_CHALS = {'mock', 'adminplz'}
GRECAPTCHA_SECRET = os.environ['GRECAPTCHA_SECRET']

kindplural = {
    'Job': 'jobs',
    'Service': 'services',
}


app = Flask(__name__)

if os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount'):
    client = K8sClient.from_serviceaccount()
else:
    client = K8sClient.from_file()


def get_challenge():
    if not request.host:
        abort(400)

    fqdn = re.match(r'^([^:]*)', request.host)
    if not fqdn:
        abort(400)
    fqdn = fqdn.group(1)

    chal = re.fullmatch(r'^([a-z]+)\.chal\.uiuc\.tf$', fqdn)
    if not chal:
        abort(404)
    chal = chal.group(1)

    if chal not in ACCEPTED_CHALS:
        abort(404)

    return chal


def check_recaptcha():
    rresponse = request.form.get('g-recaptcha-response', '')
    data = {
        'secret': GRECAPTCHA_SECRET,
        'response': rresponse
    }
    r = requests.post('https://www.google.com/recaptcha/api/siteverify',
                      data=data)
    return r.json()['success'] if r.status_code == 200 else False


@app.route('/', methods=['GET'])
def main():
    # To satisfy GKE healthcheck, see nginx.conf.
    if request.headers.get('User-Agent', '').startswith('GoogleHC/'):
        return 'Healthy'

    return render_template('main.html', title=get_challenge())


@app.route('/', methods=['POST'])
def spawn():
    challenge_name = get_challenge()
    namespace = f'{challenge_name}-managed'

    # TODO: change when ctf starts
    # if request.form.get('bypass', '') != GRECAPTCHA_SECRET:
    #     return render_template(
    #         'main.html', title=challenge_name, error='UIUCTF has not started...'), 400
    if not check_recaptcha():
        return render_template(
            'main.html', title=challenge_name, error='Failed reCaptcha, try again...'), 400

    if not client.get_objects('namespaces', f'name={namespace}'):
        return render_template(
            'main.html', title=challenge_name, error='Challenge is currently down.'), 500

    with open(f'/etc/instance-templates/{challenge_name}.yaml') as f:
        instance_template = f.read()

    while True:
        instance_name = f'inst-{secrets.token_hex(8)}'

        if client.get_objects('jobs', f'name={instance_name}',
                              namespace=namespace):
            continue

        instance = instance_template.replace('INSTANCE_NAME', instance_name)

        ownerref = None
        for doc in yaml.safe_load_all(instance):
            if 'ownerReferences' in doc['metadata']:
                assert ownerref
                doc['metadata']['ownerReferences'] = ownerref
            else:
                currentownerref = {
                    'apiVersion': doc['apiVersion'],
                    'blockOwnerDeletion': False,
                    'controller': False,
                    'kind': doc['kind'],
                    'name': doc['metadata']['name'],
                    'uid': None,
                }

            obj = client.create_object(kindplural[doc['kind']], doc,
                                       namespace=namespace)

            if 'ownerReferences' not in doc['metadata']:
                currentownerref['uid'] = obj['metadata']['uid']
                ownerref = [currentownerref]

        return redirect(f'//{instance_name}.{challenge_name}.chal.uiuc.tf')
