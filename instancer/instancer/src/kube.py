# SPDX-License-Identifier: Apache-2.0
# Copyright 2020-2022 Wikimedia Foundation and contributors
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

# This code is adapted from:
# https://github.com/wikimedia/operations-software-tools-webservice/blob/0adef7e761bb7c0b4236f6b8579fffa8b23c163e/toolsws/backends/kubernetes.py#L660
# The "T123456" notes refer to tasks as linked as
# https://phabricator.wikimedia.org/T123456

import os
import os.path

import requests
import urllib3
import yaml

# T253412: Disable warnings about unverifed TLS certs when talking to the
# Kubernetes API endpoint
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class KubernetesException(Exception):
    """Base class for exceptions related to the Kubernetes backend."""


class KubernetesConfigFileNotFoundException(KubernetesException):
    """Raised when the configuration file does not exist."""


class K8sClient(object):
    """Kubernetes API client."""

    VERSIONS = {
        "challenges": "kctf.dev/v1",
        "deployments": "apps/v1",
        "endpoints": "v1",
        "ingresses": "networking.k8s.io/v1",
        "jobs": "batch/v1",
        "namespaces": "v1",
        "pods": "v1",
        "replicasets": "apps/v1",
        "services": "v1",
    }

    @classmethod
    def from_file(cls, filename=None, **kwargs):
        """Create a client from a kubeconfig file."""
        if not filename:
            filename = os.getenv("KUBECONFIG", "~/.kube/config")
        filename = os.path.expanduser(filename)

        if not os.path.exists(filename):
            raise KubernetesConfigFileNotFoundException(filename)

        with open(filename) as f:
            data = yaml.safe_load(f.read())
        return cls.from_config(data, **kwargs)

    @classmethod
    def from_config(cls, config, *, namespace=None, **kwargs):
        self = cls(**kwargs)

        def _find_cfg_obj(kind, name):
            """Lookup a named object in our config."""
            for obj in config[kind]:
                if obj["name"] == name:
                    return obj[kind[:-1]]
            raise KeyError(
                "Key {} not found in {} section of config".format(name, kind)
            )

        context = _find_cfg_obj(
            "contexts", config["current-context"]
        )
        cluster = _find_cfg_obj("clusters", context["cluster"])
        self.server = cluster["server"]
        self.namespace = namespace or context.get("namespace", "default")

        user = _find_cfg_obj("users", context["user"])
        self.session.cert = (user["client-certificate-data"],
                             user["client-key-data"])

        return self

    @classmethod
    def from_serviceaccount(cls, *, namespace=None, **kwargs):
        self = cls(**kwargs)

        self.server = 'https://{}:{}'.format(
            os.environ['KUBERNETES_SERVICE_HOST'],
            os.environ['KUBERNETES_SERVICE_PORT_HTTPS']
        )

        sa_path = '/var/run/secrets/kubernetes.io/serviceaccount'
        with open(os.path.join(sa_path, 'token'), 'r') as f:
            self.session.headers.update({
                'Authorization': f'Bearer {f.read()}'
            })

        self.namespace = namespace
        if not namespace:
            with open(os.path.join(sa_path, 'namespace'), 'r') as f:
                self.namespace = f.read()

        return self

    def __init__(self, timeout=10):
        self.timeout = timeout
        self.session = requests.Session()
        # T253412: We are deliberately not validating the api endpoint's TLS
        # certificate. The only way to do this with a self-signed cert is to
        # pass the path to a CA bundle. We actually *can* do that, but with
        # python2 we have seen the associated clean up code fail and leave
        # /tmp full of orphan files.
        self.session.verify = False

    def _make_kwargs(self, kind, **kwargs):
        """Setup kwargs for a Requests request."""
        version = kwargs.pop("version", "v1")
        if version == "v1":
            root = "api"
        else:
            root = "apis"
        if kind == "namespaces":
            kwargs["url"] = "{}/{}/{}/namespaces".format(
                self.server, root, version
            )
        else:
            namespace = kwargs.pop("namespace", self.namespace)
            kwargs["url"] = "{}/{}/{}/namespaces/{}/{}".format(
                self.server, root, version, namespace, kind
            )
        name = kwargs.pop("name", None)
        if name is not None:
            kwargs["url"] = "{}/{}".format(kwargs["url"], name)
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout
        return kwargs

    def _get(self, kind, **kwargs):
        """GET request."""
        r = self.session.get(**self._make_kwargs(kind, **kwargs))
        r.raise_for_status()
        return r.json()

    def _post(self, kind, **kwargs):
        """POST request."""
        r = self.session.post(**self._make_kwargs(kind, **kwargs))
        r.raise_for_status()
        return r.json()

    def _delete(self, kind, **kwargs):
        """DELETE request."""
        r = self.session.delete(**self._make_kwargs(kind, **kwargs))
        r.raise_for_status()
        return r.json()

    def get_objects(self, kind, selector=None, **kwargs):
        """Get list of objects of the given kind in the namespace."""
        return self._get(
            kind,
            params={"labelSelector": selector},
            version=K8sClient.VERSIONS[kind],
            **kwargs
        )["items"]

    def delete_objects(self, kind, selector=None, **kwargs):
        """Delete objects of the given kind in the namespace."""
        if kind == "services":
            # Annoyingly Service does not have a Delete Collection option
            for svc in self.get_objects(kind, selector):
                self._delete(
                    kind,
                    name=svc["metadata"]["name"],
                    version=K8sClient.VERSIONS[kind],
                    **kwargs
                )
        else:
            self._delete(
                kind,
                params={"labelSelector": selector},
                version=K8sClient.VERSIONS[kind],
                **kwargs
            )

    def create_object(self, kind, spec, **kwargs):
        """Create an object of the given kind in the namespace."""
        return self._post(
            kind,
            json=spec,
            version=K8sClient.VERSIONS[kind],
            **kwargs
        )
