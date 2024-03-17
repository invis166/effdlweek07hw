import json
import os

import grpc
from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics
from google.protobuf.json_format import MessageToJson

import inference_pb2_grpc
import inference_pb2

INFERENCE_API_HOST = os.environ['INFERENCE_API_HOST']
INFERENCE_API_PORT = os.environ['INFERENCE_API_PORT']
APP_PORT = os.environ['APP_PORT']
APP_HOST = os.environ['APP_HOST']


app = Flask(__name__, static_url_path="")
metrics = PrometheusMetrics(app)


@app.route("/predict", methods=['POST'])
@metrics.gauge("api_in_progress", "requests in progress")
@metrics.counter("app_http_inference_count", "number of invocations")
def predict():
    url = request.get_json(force=True)['url']
    with grpc.insecure_channel(f'{INFERENCE_API_HOST}:{INFERENCE_API_PORT}') as channel:
        service = inference_pb2_grpc.InstanceDetectorStub(channel)
        resp = service.Predict(inference_pb2.InstanceDetectorInput(
            url=url
        ))

    message = MessageToJson(resp)

    return json.loads(message) or {'objects': []}


if __name__ == '__main__':
    app.run(port=APP_PORT, host=APP_HOST)
