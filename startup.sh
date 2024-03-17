#!/bin/bash

python3 client_api.py &
python3 inference_api.py &

wait
