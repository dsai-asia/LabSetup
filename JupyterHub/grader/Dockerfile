FROM jupyter/scipy-notebook:ea01ec4d9f57

ARG PROXY

USER root

# Set up proxy server. Make sure .env contains a correct PROXY var.
ENV http_proxy=$PROXY
ENV https_proxy=$PROXY

RUN apt-get update ; apt-get install -y net-tools iputils-ping
RUN conda install -c conda-forge nbgrader
RUN conda install nose
RUN conda update -n base conda

ENV http_proxy ''
ENV https_proxy ''

EXPOSE 8888

RUN echo "export http_proxy=${PROXY}" >> /home/jovyan/.bashrc
RUN echo "export https_proxy=${PROXY}" >> /home/jovyan/.bashrc

# nbgrader setup

COPY nbgrader_config_global.py /etc/jupyter/nbgrader_config.py

RUN jupyter nbextension enable --sys-prefix create_assignment/main \
 && jupyter nbextension enable --sys-prefix formgrader/main --section=tree \
 && jupyter serverextension enable --sys-prefix nbgrader.server_extensions.formgrader

WORKDIR /home/grader-at82.03

