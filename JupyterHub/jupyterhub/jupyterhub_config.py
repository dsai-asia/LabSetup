
# JupyterHub configuration for DSAI lab server machines

import os
import ldapauthenticator
import logging
import requests
from jupyterhub import orm

logger = logging.getLogger()
logger.setLevel(logging.INFO)

c = get_config()

# General

c.JupyterHub.admin_access = True
c.JupyterHub.hub_ip = os.environ['HUB_IP']
# c.JupyterHub.hub_ip = 'jupyterhub'
# c.JupyterHub.hub_port = 8080
c.JupyterHub.cookie_secret_file = '/persist/jupyterhub_cookie_secret'
c.JupyterHub.db_url = '/persist/jupyterhub.sqlite'
c.JupyterHub.cleanup_servers = False

# Function to query database to get members of a course's instructor group

def _get_instructor_users(db, course_id):
    """Get users that are a member of the instructor/grader group"""
    logger.info('Getting instructor users for %s', course_id)
    group_name = 'formgrade-%s' % course_id
    group = orm.Group.find(db, name=group_name)
    if group is None:
        return []
    else:
        return [ u.name for u in group.users ]


# Custom authenticator that looks up learner/instructor status before spawn

class CustomAuthenticator(ldapauthenticator.LDAPAuthenticator):

    def pre_spawn_start(self, user, spawner):
        logger.info('Prespawn for user ' + user.name)
        user.spawner.environment['USER_ROLE'] = 'Learner'
        token = os.environ.get('JUPYTERHUB_API_TOKEN')
        course_id = spawner.user_options['image']
        instructors = _get_instructor_users(spawner.db, course_id)
        spawner.volumes['jupyterhub_nbgrader_exchange'] = '/srv/nbgrader/exchange'
        if user.name in instructors:
            user.spawner.environment['USER_ROLE'] = 'Instructor'
            logger.info('User has Instructor role')
            grader_home = 'jupyterhub_nbgrader_%s_home' % course_id.lower().replace('.', '_')
            spawner.volumes[grader_home] = '/home/%s/nbgrader' % user.name
        return

# Authentication (CHANGE FOR YOUR NETWORK SETUP)

c.JupyterHub.authenticator_class = CustomAuthenticator
c.LDAPAuthenticator.server_address = 'ldap.cs.ait.ac.th'
c.LDAPAuthenticator.bind_dn_template = [ "uid={username},ou=People,ou=csim,dc=cs,dc=ait,dc=ac,dc=th" ]

# General DockerSpawner configuration

c.DockerSpawner.debug = True
c.DockerSpawner.use_internal_ip = True
network_name = os.environ['DOCKER_NETWORK_NAME']
c.DockerSpawner.network_name = network_name
# The image list is in classes.json (loaded below)
# c.DockerSpawner.image_whitelist = { 'SciPy': 'jupyterhub_lab', ... }

c.DockerSpawner.remove_containers = True
c.DockerSpawner.remove = True
# c.DockerSpawner.remove_containers = False
# c.DockerSpawner.remove = False
from jupyter_client.localinterfaces import public_ips
c.DockerSpawner.hub_ip_connect = public_ips()[0]

spawn_cmd = "start-singleuser.sh --SingleUserNotebookApp.default_url=/lab --SingleUserNotebookApp.disable_user_config=True"
c.DockerSpawner.extra_create_kwargs.update({ 'command': spawn_cmd })

# JupyterLab setup

notebook_dir = '/home/{username}/work'
c.DockerSpawner.notebook_dir = notebook_dir
c.DockerSpawner.volumes = {
  'jupyterhub-user-{username}': notebook_dir,
}
c.Spawner.default_url = '/lab'
c.DockerSpawner.extra_host_config = {
#    'network_mode': network_name,
    'shm_size': '1g'
}

# Give spawned containers access to the GPUs. We
# override the default DockerSpawner to request access to the GPUs
# using docker-py's host_config DeviceRequests

from dockerspawner import DockerSpawner

class CustomSpawner(DockerSpawner):

    def get_env(self):
        env = super().get_env()
        env['NB_USER'] = env['NB_GROUP'] = self.user.name
        env['NOTEBOOK_DIR'] = '.' if env['USER_ROLE'] == 'Instructor' else 'work'
        env['COURSE_NAME'] = self.user_options['image']
        env['COURSE_HOME_ON_CONTAINER'] = os.path.join('/home', env['NB_USER'], env['NOTEBOOK_DIR'], env['COURSE_NAME'])
        env['IS_INSTRUCTOR'] = 'true' if env['USER_ROLE'] == 'Instructor' else 'false'
        return env

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
                c.JupyterHub.services.append(service)
                print('Service: ' + service['name'])
    if data['DockerSpawner']:
        if data['DockerSpawner']['image_whitelist']:
            c.DockerSpawner.allowed_images = data['DockerSpawner']['image_whitelist']

