
import os
import re
from traitlets.log import get_logger
from nbgrader.auth import JupyterHubAuthPlugin

logger = get_logger()
c = get_config()

c.Exchange.path_includes_course = True
c.Exchange.root = '/srv/nbgrader/exchange'
c.NbGrader.logfile = '/usr/local/share/jupyter/nbgrader.log'

c.IncludeHeaderFooter.header = 'source/header.ipynb'
c.CourseDirectory.ignore = [ '.ipynb_checkpoints' ]
c.CourseDirectory.include = [ '*.ipynb', '*.csv', '*.png', '*.jpg', '*.txt' ]

c.Authenticator.plugin_class = JupyterHubAuthPlugin

user = os.environ['NB_USER']
# c.CourseDirectory.root = '/home/%s/nbgrader/%s' % (user, course_id)
c.CourseDirectory.root = '/home/%s/nbgrader' % user

# Get course ID

m = re.match('grader-(.*)$', user) if user else None
if m is None:
    logger.warn('Cannot determine course ID')
else:
    course_id = m[1].upper()
    c.CourseDirectory.course_id = course_id

#c.CourseDirectory.root = '/home/grader-AT82.03/AT82.03'
#c.ExchangeFetchAssignment.assignment_dir = '/home/%s/work' % user
#c.Exchange.assignment_dir = '/home/%s/work' % user

os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

