FROM jupyter/scipy-notebook:ea01ec4d9f57

ARG PROXY

USER root

# Set up proxy server. Make sure .env contains a correct PROXY var.
ENV http_proxy=$PROXY
ENV https_proxy=$PROXY

RUN apt-get update ; apt-get install -y net-tools iputils-ping

ENV http_proxy ''
ENV https_proxy ''

USER jovyan
EXPOSE 8888

RUN echo "export http_proxy=${PROXY}" >> /home/jovyan/.bashrc
RUN echo "export https_proxy=${PROXY}" >> /home/jovyan/.bashrc

