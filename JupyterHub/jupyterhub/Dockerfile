# Do not forget to pin down the version
FROM jupyterhub/jupyterhub:1.4.2

ARG PROXY

# Set up proxy server. Make sure .env contains a correct PROXY var.
ENV http_proxy=$PROXY
ENV https_proxy=$PROXY

# Install some useful OS packages
RUN apt-get update && \
    apt-get install -y wget net-tools iputils-ping git

# Reinstall JupyterHub to make sure everything is in place
RUN pip install --upgrade pip
RUN pip install --force --no-deps jupyterhub==1.4.2

# Install packages needed for JupyterHub setup (authentication and spawning)
RUN pip install \
    dockerspawner==12.1.0 \
    oauthenticator==0.11.0 \
    jupyterhub-ldapauthenticator==1.3.0 \
    jupyter-client==6.1.6 \
    netifaces \
    jupyterhub-idle-culler==1.0

# Install packages for teaching
RUN pip install nbgrader

# Proxy should not be used during operation (all JupyterHub activity is local)
ENV http_proxy ''
ENV https_proxy ''

# Copy top-level page template into the container
COPY jupyterhub-page-template.html /usr/local/share/jupyterhub/templates/page.html

# Copy the JupyterHub configuration into the container
COPY jupyterhub_config.py .
#COPY jupyterhub_config.json .
COPY classes.json .

