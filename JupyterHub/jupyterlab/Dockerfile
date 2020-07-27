FROM jupyter/scipy-notebook:ea01ec4d9f57

USER root

ENV http_proxy http://192.41.170.23:3128
ENV https_proxy http://192.41.170.23:3128
RUN apt-get update ; apt-get install -y net-tools iputils-ping

ENV http_proxy ''
ENV https_proxy ''

USER jovyan
EXPOSE 8888

RUN echo "export http_proxy=http://192.41.170.23:3128" >> /home/jovyan/.bashrc
RUN echo "export https_proxy=http://192.41.170.23:3128" >> /home/jovyan/.bashrc

