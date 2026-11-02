import cv2
import torch
from PIL import Image

from train import EVAL_TF, MODEL, build


class CandyModel:
    def __init__(self, path=MODEL):
        ckpt = torch.load(path)
        self.classes = ckpt["classes"]
        self.net = build(len(self.classes))
        self.net.load_state_dict(ckpt["state"])
        self.net.eval()

    def predict(self, crop_bgr):
        x = EVAL_TF(Image.fromarray(cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)))[None]
        with torch.no_grad():
            probs = torch.softmax(self.net(x), 1)[0]
        i = int(probs.argmax())
        return self.classes[i], float(probs[i])
