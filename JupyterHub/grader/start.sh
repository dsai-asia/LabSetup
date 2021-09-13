#!/bin/bash

set -e

echo "Executing custom start.sh"

# Exec the specified command or fall back on bash
if [ $# -eq 0 ]; then
    cmd=( "bash" )
else
    cmd=( "$@" )
fi

echo "ID: `id -u`"

if [[ "$NB_USER" == "jovyan" ]]; then
    echo "We need to have hub usernames for nbgrader to work instead of static user jovyan."
    exit 1
fi

mount | grep jovyan && {
    echo "Incorrect mount under /home/jovyan."
    exit 1
}

if [[ $(id -u) != 0 ]]; then
    echo "We need root privilege to set up nbgrader"
    exit 1
fi

userdel -rf jovyan
rm -rf /home/jovyan

# Add user and group.
if id "${NB_USER}" >/dev/null 2>&1; then
    echo "User ${NB_USER} exists."
else
    echo "User does not exist. Adding user ${NB_USER} (${NB_UID})"
    # User home directory will already exist because DockerSpawner mounted a docker volume at /home/$NB_USER
    useradd -d /home/${NB_USER} -u ${NB_UID} -g ${NB_GID} ${NB_USER}
fi

mkdir -p /home/${NB_USER}/${NOTEBOOK_DIR}
mkdir -p /home/${NB_USER}/.jupyter
chown -R $NB_UID:$NB_GID /home/$NB_USER
cd /home/$NB_USER

chown ${NB_UID}:${NB_GID} /srv/nbgrader/exchange
chmod 777 /srv/nbgrader/exchange

# Enable sudo if requested
if [[ "$GRANT_SUDO" == "1" || "$GRANT_SUDO" == 'yes' ]]; then
    echo "Granting $NB_USER sudo access and appending $CONDA_DIR/bin to sudo PATH"
    echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/notebook
fi

# Add $CONDA_DIR/bin to sudo secure_path
sed -r "s#Defaults\s+secure_path\s*=\s*\"?([^\"]+)\"?#Defaults secure_path=\"\1:$CONDA_DIR/bin\"#" /etc/sudoers | grep secure_path > /etc/sudoers.d/path

# Exec the command as NB_USER with the PATH and the rest of the environment preserved
echo "Executing the command: ${cmd[@]}"
exec sudo -E -H -u $NB_USER PATH=$PATH XDG_CACHE_HOME=/home/$NB_USER/.cache PYTHONPATH=${PYTHONPATH:-} "${cmd[@]}"

