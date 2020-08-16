
# JupyterHub configuration for DSAI lab server machines

import os

c = get_config()

# General

c.JupyterHub.admin_access = True
c.JupyterHub.hub_ip = os.environ['HUB_IP']
c.JupyterHub.cookie_secret_file = '/persist/jupyterhub_cookie_secret'
c.JupyterHub.db_url = '/persist/jupyterhub.sqlite'
c.JupyterHub.cleanup_servers = False

# Authentication (CHANGE FOR YOUR NETWORK SETUP)

c.JupyterHub.authenticator_class = 'ldapauthenticator.LDAPAuthenticator'
c.LDAPAuthenticator.server_address = 'ldap.cs.ait.ac.th'
c.LDAPAuthenticator.bind_dn_template = [ "uid={username},ou=People,ou=csim,dc=cs,dc=ait,dc=ac,dc=th" ]

# General DockerSpawner configuration

c.DockerSpawner.debug = True
c.DockerSpawner.network_name = os.environ['DOCKER_NETWORK_NAME']
c.DockerSpawner.image_whitelist = { 'SciPy': 'jupyterhub_lab',
                                    'SciPy+CUDA': 'jupyterhub_lab_cuda',
                                    'SciPy+CUDA+NLTK': 'jupyterhub_lab_cuda_nltk' }

c.DockerSpawner.remove_containers = True
from jupyter_client.localinterfaces import public_ips
c.DockerSpawner.hub_ip_connect = public_ips()[0]

# JupyterLab setup

notebook_dir = '/home/jovyan/work'
c.DockerSpawner.notebook_dir = notebook_dir
c.DockerSpawner.volumes = { 'jupyterhub-user-{username}': notebook_dir }
c.Spawner.default_url = '/lab'

# Give spawned containers access to the GPUs. We
# override the default DockerSpawner to request access to the GPUs
# using docker-py's host_config DeviceRequests

from dockerspawner import DockerSpawner

class CustomSpawner(DockerSpawner):

    def docker(self, method, *args, **kwargs):
        if method == 'create_container':
            kwargs['host_config']['DeviceRequests'] = [{
                'Driver': '',
                'Count': -1,
                'DeviceIDs': None,
                'Capabilities': [ ['gpu'] ],
                'Options': {} } ]
        return super().docker(method, *args, **kwargs)

c.JupyterHub.spawner_class = CustomSpawner

# Cull idle single-user servers after 1 hour

import sys
c.JupyterHub.services = [
    {
        'name': 'idle-culler',
        'admin': True,
        'command': [
            sys.executable, '-m',
            'jupyterhub_idle_culler', '--timeout=3600'
        ],
    }
]

import json
with open('classes.json') as json_file:
    data = json.load(json_file)
    if data['Authenticator']:
        c.Authenticator.admin_users = data['Authenticator']['admin_users']
    if data['JupyterHub']:
        if data['JupyterHub']['load_groups']:
            c.JupyterHub.load_groups = data['JupyterHub']['load_groups']
        if data['JupyterHub']['services']:
            for service in data['JupyterHub']['services']:
                #c.JupyterHub.services.append(service)
                print('Service: ' + service['name'])
    if data['DockerSpawner']:
        if data['DockerSpawner']['image_whitelist']:
            c.DockerSpawner.image_whitelist = data['DockerSpawner']['image_whitelist']

