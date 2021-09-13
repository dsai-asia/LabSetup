FROM jupyter/scipy-notebook:ea01ec4d9f57

ARG PROXY

USER root

# Set up proxy server. Make sure .env contains a correct PROXY var.
ENV http_proxy=$PROXY
ENV https_proxy=$PROXY

RUN apt-get update ; apt-get install -y net-tools iputils-ping

USER $NB_UID
WORKDIR /home/$NB_USER

RUN conda install jupyterhub=1.4.2 && \
    conda install -c conda-forge nbgrader && \
    conda install nose && \
    conda update -n base conda && \
    fix-permissions $CONDA_DIR

ENV http_proxy ''
ENV https_proxy ''

EXPOSE 8888

RUN echo "export http_proxy=${PROXY}" >> /home/jovyan/.bashrc
RUN echo "export https_proxy=${PROXY}" >> /home/jovyan/.bashrc

# nbgrader setup

COPY nbgrader_config_global.py /etc/jupyter/nbgrader_config.py

USER root
RUN mkdir -p /usr/local/share/jupyter && chmod 777 /usr/local/share/jupyter

USER $NB_UID

RUN jupyter nbextension enable --sys-prefix create_assignment/main \
 && jupyter nbextension enable --sys-prefix formgrader/main --section=tree \
 && jupyter serverextension enable --sys-prefix nbgrader.server_extensions.formgrader \
 && jupyter nbextension disable --sys-prefix assignment_list/main --section=tree \
 && jupyter nbextension disable --sys-prefix course_list/main --section=tree \
 && jupyter serverextension disable --sys-prefix nbgrader.server_extensions.assignment_list \
 && jupyter serverextension disable --sys-prefix nbgrader.server_extensions.course_list

USER root
WORKDIR /root
COPY start.sh /usr/local/bin
COPY jupyter_notebook_config.py /etc/jupyter

