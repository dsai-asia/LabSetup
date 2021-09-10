
from nbgrader.auth import JupyterHubAuthPlugin

c = get_config()

c.Exchange.path_includes_course = True
c.Exchange.root = '/srv/nbgrader/exchange'
c.Authenticator.plugin_class = JupyterHubAuthPlugin
# c.NbGrader.logfile = '/usr/local/share/jupyter/nbgrader.log'

