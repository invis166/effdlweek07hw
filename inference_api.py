import os
import io
import logging
from concurrent import futures

import torch
import requests
import grpc
import torchvision.transforms as transforms
from torchvision.models.detection import MaskRCNN_ResNet50_FPN_Weights, maskrcnn_resnet50_fpn
from PIL import Image

import inference_pb2
import inference_pb2_grpc


INFENRENCE_API_PORT = os.environ['INFERENCE_API_PORT']

THRESHOLD = 0.75

transforms = MaskRCNN_ResNet50_FPN_Weights.COCO_V1.transforms()


def get_image_from_url(url: str):
    resp = requests.get(url)
    image = Image.open(io.BytesIO(resp.content))
    img_data = transforms(image).unsqueeze(0)

    return img_data


class InferenceDetector(inference_pb2_grpc.InstanceDetector):
    def __init__(self):
        self.categories = MaskRCNN_ResNet50_FPN_Weights.DEFAULT.meta['categories']
        self.model = maskrcnn_resnet50_fpn(weights=MaskRCNN_ResNet50_FPN_Weights.DEFAULT)
        self.model.eval()

    def Predict(self, request, context):
        url = request.url
        image = get_image_from_url(url)
        with torch.no_grad():
                model_out = self.model(image)[0]
        scores = model_out['scores']
        object_idx = model_out['labels'][(scores > THRESHOLD).nonzero().flatten()]
        object_names = [self.categories[idx] for idx in object_idx]

        return inference_pb2.InstanceDetectorOutput(objects=object_names)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    inference_pb2_grpc.add_InstanceDetectorServicer_to_server(InferenceDetector(), server)
    server.add_insecure_port(f'[::]:{INFENRENCE_API_PORT}')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    print("start serving...")
    serve()
