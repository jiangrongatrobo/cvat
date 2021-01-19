# from pathlib import Path

import cv2
import torch

from models.experimental import attempt_load
from utils.datasets import letterbox
from utils.general import non_max_suppression, scale_coords

from PIL import Image
from io import BytesIO
import base64
import cv2
import os
import yaml
import json
import numpy as np

class ModelLoader:
  def __init__ (self, model_path: str, spec_file: str):
    self.device = 'cpu'
    self.model = attempt_load(model_path, map_location=self.device)  # load FP32 model
    labels = {item['id']: item['name'] for item in json.loads(yaml.safe_load(open(spec_file))['metadata']['annotations']['spec'])}
    spec_names = [each[1] for each in sorted(labels.items(), key = lambda x:x[0])]

    self.names = self.model.module.names if hasattr(self.model, 'module') else self.model.names
    for namea, nameb in zip(spec_names, self.names):
      assert namea == nameb, "check classes name: {} {}".format(namea, nameb)

  def __del__(self):
    del self.model

  def infer(self, im_data: str, from_request: bool = False):
    ret = []
    try:
      if from_request:
        out_buf = BytesIO(base64.b64decode(im_data.encode('utf-8')))
        origin_image = Image.open(out_buf)
        height = origin_image.height
        width = origin_image.width
        origin_image = np.array(origin_image.getdata())
        channel = 1 if len(origin_image.shape) == 1 else 3
        origin_image = origin_image.reshape((height, width, channel)).astype(np.uint8)
        if channel == 1:
          origin_image = np.concatenate([origin_image,origin_image,origin_image], axis=-1)
        origin_image = cv2.cvtColor(origin_image, cv2.COLOR_RGB2BGR)
      else:
        origin_image = cv2.imread(im_data)

      img0 = origin_image
      # Padded resize
      tgt_img_size = 640
      img = letterbox(img0, new_shape=tgt_img_size)[0]
      # Convert
      img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to CHW
      img = np.ascontiguousarray(img)

      # for path, img, im0s, _ in dataset:
      img = torch.from_numpy(img).to(self.device)
      img = img.float()  # uint8 to fp32
      img /= 255.0  # 0 - 255 to 0.0 - 1.0
      if img.ndimension() == 3:
          img = img.unsqueeze(0)

      # Inference
      pred = self.model(img, augment=False)[0]

      # Apply NMS
      conf_thres = 0.25
      iou_thres = 0.45
      classes=None
      agnostic_nms=False
      pred = non_max_suppression(pred, conf_thres, iou_thres, classes=classes, agnostic=agnostic_nms)

      det = pred[0]

      if len(det):
          # Rescale boxes from img_size to im0 size
          det[:, :4] = scale_coords(img.shape[2:], det[:, :4], img0.shape).round()
          for box in reversed(det).numpy():
            x1,y1,x2,y2,score,clsid = box
            x1,y1,x2,y2,score,class_name = int(float(x1)),int(float(y1)),int(float(x2)),int(float(y2)),str(float(score)),self.names[int(clsid)]
            ret.append({
              "confidence": score,
              "label": class_name,
              "points": [x1,y1,x2,y2],
              "type": "rectangle",
            })
      print(ret)
    except Exception as e:
      print(str(e))
    return ret


if __name__ == "__main__":
  sess = ModelLoader('./ir.pt', './ir.yaml')
  img_path = "./images/001424.jpg"
  # sess = ModelLoader('./baiguang.pt', './baiguang.yaml')
  # img_path = "./images/StereoVision_L_148889_10_0_1_893_D_Fan_1840_135_WholeFan_1772_198.jpeg"
  _ = sess.infer(img_path, False)
  print("==================================")
  in_buf = BytesIO()
  Image.open(img_path).save(in_buf, 'jpeg') # JPEG compression might slightly make detections changed.
  request_data = base64.b64encode(in_buf.getvalue()).decode('utf-8')
  _ = sess.infer(request_data, True)
