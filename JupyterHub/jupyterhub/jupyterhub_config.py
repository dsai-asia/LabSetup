
# JupyterHub configuration for DSAI lab machines

import os

c = get_config()

# General

c.JupyterHub.admin_access = True
c.JupyterHub.hub_ip = os.environ['HUB_IP']

# Authentication (CHANGE FOR YOUR NETWORK SETUP)

c.JupyterHub.authenticator_class = 'ldapauthenticator.LDAPAuthenticator'
c.LDAPAuthenticator.server_address = 'ldap.cs.ait.ac.th'
c.LDAPAuthenticator.bind_dn_template = [ "uid={username},ou=People,ou=csim,dc=cs,dc=ait,dc=ac,dc=th" ]
c.Authenticator.admin_users = { 'mdailey' }

# General DockerSpawner configuration

c.DockerSpawner.debug = True
c.DockerSpawner.network_name = os.environ['DOCKER_NETWORK_NAME']
c.DockerSpawner.image_whitelist = { 'SciPy': 'jupyterhub_lab',
                                    'SciPy+CUDA': 'jupyterhub_lab_cuda' }
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

#c.JupyterHub.services = [
#    {
#        'name': 'cull_idle',
#        'admin': True,
#        'command': 'python /srv/jupyterhub/cull_idle_servers.py --timeout=3600'.split(),
#    },
#]

