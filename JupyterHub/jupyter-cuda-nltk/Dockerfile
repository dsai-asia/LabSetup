
FROM jupyterhub_lab_cuda

ARG PROXY

# Set up proxy server. Make sure .env contains a correct PROXY var.
ENV http_proxy=$PROXY
ENV https_proxy=$PROXY

RUN pip install nltk

ENV http_proxy ''
ENV https_proxy ''

WORKDIR /root

