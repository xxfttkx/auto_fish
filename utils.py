# utils.py

from datetime import datetime
import os
import cv2
from config import LOG_DIR

def ensure_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

def save_screenshot(img, filename):
    filename+= '_'+datetime.now().strftime("%Y%m%d_%H%M%S")+'.png'
    ensure_log_dir()
    filepath = os.path.join(LOG_DIR, filename)
    cv2.imwrite(filepath, img)
    print("保存路径：", os.path.abspath(filepath))
