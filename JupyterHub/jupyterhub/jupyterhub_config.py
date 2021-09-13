
# JupyterHub configuration for DSAI lab server machines

import os
import ldapauthenticator
import logging
import requests
from jupyterhub import orm
import json
import re
from tornado import gen

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

def _get_student_users(db, course_id):
    """Get users that are a member of the student group"""
    logger.info('Getting student users for %s', course_id)
    group_name = 'nbgrader-%s' % course_id
    group = orm.Group.find(db, name=group_name)
    if group is None:
        return []
    else:
        return [ u.name for u in group.users ]

# Custom authenticator that looks up learner/instructor status before spawn

class CustomAuthenticator(ldapauthenticator.LDAPAuthenticator):
 
    @gen.coroutine
    def pre_spawn_start(self, user, spawner):
        logger.info('-------------- Prespawn for user ' + user.name + ' ------------------------')
        auth_state = yield user.get_auth_state()
        logger.info(auth_state)
        user.spawner.environment['NB_UID'] = auth_state['uidNumber'][0]
        course_id = spawner.user_options['image']
        instructors = _get_instructor_users(spawner.db, course_id)
        students = _get_student_users(spawner.db, course_id)
        if user.name in instructors:
            logger.info('User is instructor')
            spawner.volumes['jupyterhub_nbgrader_exchange'] = '/srv/nbgrader/exchange'
            if re.match('grader-', user.name):
                user.spawner.environment['USER_ROLE'] = 'Grader'
            else:
                user.spawner.environment['USER_ROLE'] = 'Instructor'
            grader_home = 'jupyterhub_nbgrader_%s_home' % course_id.lower().replace('.', '_')
            spawner.volumes[grader_home] = '/home/%s/nbgrader' % user.name
        elif user.name in students:
            logger.info('User is student')
            spawner.volumes['jupyterhub_nbgrader_exchange'] = '/srv/nbgrader/exchange'
            user.spawner.environment['USER_ROLE'] = 'Learner'
        else:
            user.spawner.environment['USER_ROLE'] = None

# Authentication (CHANGE FOR YOUR NETWORK SETUP)

c.JupyterHub.authenticator_class = CustomAuthenticator
c.LDAPAuthenticator.server_address = 'ldap.cs.ait.ac.th'
c.LDAPAuthenticator.bind_dn_template = [ "uid={username},ou=People,ou=csim,dc=cs,dc=ait,dc=ac,dc=th" ]
c.Authenticator.enable_auth_state = True
c.LDAPAuthenticator.auth_state_attributes = [ 'uid', 'uidNumber' ]

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
        # env['JUPYTER_SERVER_ROOT'] = '/home/%s' % self.user.name
        if env['USER_ROLE'] == 'Instructor' or env['USER_ROLE'] == 'Grader':
            env['NOTEBOOK_DIR'] = '.'
        else:
            env['NOTEBOOK_DIR'] = 'work'
        if env['USER_ROLE']:
            env['COURSE_NAME'] = self.user_options['image']
            courses_root = 'work' if env['NOTEBOOK_DIR'] == '.' else env['NOTEBOOK_DIR']
            env['COURSE_HOME_ON_CONTAINER'] = os.path.join('/home', env['NB_USER'], courses_root, env['COURSE_NAME'])
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

all_images = None
def allowed_images(spawner):
    logger.info('Getting images for ' + spawner.user.name)
    match = re.match('grader-(.*)$', spawner.user.name)
    if match:
        course_id = match[1].upper()
        image = 'jupyterhub_lab_%s' % match[1].replace('.', '_')
        return { course_id: image }
    else:
        return all_images

with open('classes.json') as json_file:
    data = json.load(json_file)
    if data['Authenticator']:
        c.Authenticator.admin_users = data['Authenticator']['admin_users']
    if data['JupyterHub']:
        if data['JupyterHub']['load_groups']:
            c.JupyterHub.load_groups = data['JupyterHub']['load_groups']
        if data['JupyterHub']['services']:
            for service in data['JupyterHub']['services']:
                service['api_token'] = os.environ['JUPYTERHUB_API_TOKEN']
                c.JupyterHub.services.append(service)
                print('Service: ' + service['name'])
    if data['DockerSpawner']:
        if data['DockerSpawner']['image_whitelist']:
            all_images = data['DockerSpawner']['image_whitelist']
            c.DockerSpawner.allowed_images = allowed_images


