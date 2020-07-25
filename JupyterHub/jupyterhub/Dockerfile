
# Do not forget to pin down the version
FROM jupyterhub/jupyterhub:1.1.0

# Set up for proxy at AIT/CSIM (CHANGE THIS FOR YOUR NETWORK)
ENV http_proxy http://192.41.170.23:3128
ENV https_proxy http://192.41.170.23:3128

# Install some useful OS packages
RUN apt-get update && apt-get install -y wget net-tools iputils-ping git

# Copy the JupyterHub configuration into the container
COPY jupyterhub_config.py .

# Reinstall JupyterHub to make sure everything is in place
RUN pip install --upgrade pip
RUN pip install --force --no-deps jupyterhub==1.1.0

# Install packages needed for JupyterHub setup (authentication and spawning)
RUN pip install \
    dockerspawner==0.11.1 \
    oauthenticator==0.11.0 \
    jupyterhub-ldapauthenticator==1.3.0 \
    jupyter-client==6.1.6 \
    netifaces \
    jupyterhub-idle-culler

# Install packages for teaching
RUN pip install nbgrader

# Proxy should not be used during operation (all JupyterHub activity is local)
ENV http_proxy ''
ENV https_proxy ''

