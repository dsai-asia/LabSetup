
FROM jupyterhub_lab_cuda_nltk

# USER $NB_UID

ARG PROXY

ENV http_proxy=$PROXY
ENV https_proxy=$PROXY
 
COPY segmentation.py /opt/pytorch/vision/torchvision/models/segmentation/
COPY segmentation.py /opt/conda/lib/python3.8/site-packages/torchvision/models/segmentation/

COPY _utils.py /opt/pytorch/vision/torchvision/models/segmentation/
COPY _utils.py /opt/conda/lib/python3.8/site-packages/torchvision/models/segmentation/

COPY mobilenetv2.py /opt/pytorch/vision/torchvision/models/
COPY mobilenetv2.py /opt/conda/lib/python3.8/site-packages/torchvision/models/

COPY mobilenetv3.py /opt/pytorch/vision/torchvision/models/
COPY mobilenetv3.py /opt/conda/lib/python3.8/site-packages/torchvision/models/

COPY lraspp.py /opt/pytorch/vision/torchvision/models/segmentation/
COPY lraspp.py /opt/conda/lib/python3.8/site-packages/torchvision/models/segmentation/

# RUN fix-permissions $CONDA_DIR

# RUN echo "Proxy: $http_proxy"

RUN pip install pycocotools

ENV http_proxy=
ENV https_proxy=

WORKDIR /root

