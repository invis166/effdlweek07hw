FROM python:3.7

RUN mkdir -p /root/.cache/torch/hub/checkpoints && \
  wget https://download.pytorch.org/models/maskrcnn_resnet50_fpn_coco-bf2d0c1e.pth -O \
  /root/.cache/torch/hub/checkpoints/maskrcnn_resnet50_fpn_coco-bf2d0c1e.pth

COPY requirements.txt .
RUN pip3 install -r requirements.txt

RUN mkdir /app
WORKDIR /app

COPY protos /app/protos
COPY *.py /app/
COPY startup.sh /app/
RUN python3 run_codegen.py

ARG INFERENCE_API_PORT
ARG INFERENCE_API_HOST
ARG APP_HOST
ARG APP_PORT

ENV INFERENCE_API_PORT=50051
ENV INFERENCE_API_HOST=0.0.0.0
ENV APP_HOST=0.0.0.0
ENV APP_PORT=8080

ENTRYPOINT ["/app/startup.sh"]
