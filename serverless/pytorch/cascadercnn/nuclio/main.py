import json
import base64
from PIL import Image
import os
import io
# from model_handler import ModelHandler
from model_loader import ModelLoader

def init_context(context):
    context.logger.info("Init context...  0%")

    # Read the DL model
    model = ModelLoader(os.getenv('cascadeRCNNConfig'), os.getenv('cascadeRCNNModel'), device=os.getenv('cascadeRCNNDevice'))
    setattr(context.user_data, 'model', model)

    context.logger.info("Init context...100%")

def handler(context, event):
    context.logger.info("Run cascadercnn model")
    data = event.body

    results = context.user_data.model.infer(data["image"], 0.3, True, os.getenv('is_ir')=='1')

    return context.Response(body=json.dumps(results), headers={},
        content_type='application/json', status_code=200)