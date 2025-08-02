import time
import keyboard
from window_util import *
from color_util import *

import cv2
import numpy as np

def match_add_rod(full_img, template_path, roi_scale=(0.75, 0.75), match_method=cv2.TM_CCOEFF_NORMED):
    """
    在 full_img 的右下角区域中，匹配 template_path 图像，返回 best_score。

    参数:
        full_img: 当前窗口截图（BGR）
        template_path: 模板图像路径（add_rod.png）
        roi_scale: 匹配区域占整张图像的宽高比例 (width%, height%)，默认右下角 25%
        match_method: OpenCV 匹配方法，默认 TM_CCOEFF_NORMED

    返回:
        best_score: 匹配得分（0~1）
    """
    # 加载并灰度化模板
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        raise FileNotFoundError(f"未找到模板文件: {template_path}")
    template_h, template_w = template.shape

    # 转为灰度图
    full_gray = cv2.cvtColor(full_img, cv2.COLOR_BGR2GRAY)
    h, w = full_gray.shape

    # 定义右下角搜索区域（比例裁剪）
    roi_x = int(w * (1 - roi_scale[0]))
    roi_y = int(h * (1 - roi_scale[1]))
    roi = full_gray[roi_y:h, roi_x:w]

    # 匹配
    res = cv2.matchTemplate(roi, template, match_method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    best_score = max_val if match_method in [cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR_NORMED] else -min_val

    return best_score


def check_and_replace_rod(full_img, width, height, hwnd, window):
    """
    检查鱼竿是否无耐久，如果是则执行换竿流程。

    参数:
        full_img: 当前全屏截图
        width, height: 屏幕尺寸
        hwnd: 窗口句柄
        window: 窗口对象（如 pygetwindow 获取的）

    返回:
        True 表示已进行换竿，False 表示不需要换
    """
    need_change_rod = match_add_rod(full_img,"assets/add_rod.png")

    log(f"need_change_rod.score = {need_change_rod}")
    if need_change_rod<0.9:
        return False

    log("鱼竿没耐久了，换杆")

    # 第一步：模拟按键
    keyboard.press(ROD_NO_DURABILITY_KEY)
    time.sleep(0.05)
    keyboard.release(ROD_NO_DURABILITY_KEY)
    time.sleep(ROD_NO_DURABILITY_DELAY)

    # 第二步：点击更换位置
    window.activate()
    click_mouse_window(hwnd, *ROD_CHANGE_CLICK_POS)
    time.sleep(ROD_NO_DURABILITY_DELAY)

    # 第三步：点击确认
    window.activate()
    click_mouse_window(hwnd, *ROD_CONFIRM_CLICK_POS)
    time.sleep(ROD_NO_DURABILITY_DELAY)

    return True
