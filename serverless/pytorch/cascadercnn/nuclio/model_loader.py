from PIL import Image
from io import BytesIO
import base64
import cv2
import numpy as np

from mmdet.apis import inference_detector, init_detector
from mmdet.datasets import DetDataset, DetDataset_ir
class ModelLoader:
  def __init__ (self, config, model, device):
    self.MODEL = init_detector(config, model, device)
    if hasattr(self.MODEL, 'module'):
      self.MODEL = self.MODEL.module

  def __del__(self):
    del self.MODEL

  def infer(self, im_data: str, score_thr:float, from_request: bool = False, is_ir: bool = False):
    # print(im_data)
    if is_ir:
        classes_name = DetDataset_ir.CLASSES
    else:
        classes_name = DetDataset.CLASSES
    if from_request:
      out_buf = BytesIO(base64.b64decode(im_data.encode('utf-8')))
      origin_image = Image.open(out_buf)
      origin_image = np.array(origin_image.getdata()).reshape((origin_image.height, origin_image.width, 3)).astype(np.uint8)
      origin_image = cv2.cvtColor(origin_image, cv2.COLOR_RGB2BGR)
    else:
      origin_image = cv2.imread(im_data)
    h, w, _ = origin_image.shape
    outputs = inference_detector(self.MODEL, origin_image)
    dets = []
    for cls_id, boxes in enumerate(outputs):
            cls_name = classes_name[cls_id]
            scores = boxes[:, -1]
            boxes = np.round(boxes[:, :-1]).astype(int)
            for score, box in zip(scores, boxes):
                if score < score_thr:
                    continue
                x1, y1, x2, y2 = box
                dets.append({
                  "confidence": str(score),
                  "label": cls_name,
                  "points": [str(x1),str(y1),str(x2),str(y2)],
                  "type": "rectangle",
                })
    print(dets)
    return dets


