# color_util.py

import numpy as np
import cv2
from config import *

def is_red_dominant(roi, threshold=0.6):
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)
    red_pixel_count = cv2.countNonZero(mask)
    total_pixels = roi.shape[0] * roi.shape[1]
    red_ratio = red_pixel_count / total_pixels
    return red_ratio >= threshold

def find_max_red_region(img, search_rect, box_size=7, threshold=RED_THRESHOLD):
    """
    在指定大区域内滑动窗口，找到红色像素比例最高的小区域
    返回 (x1, y1, x2, y2), max_ratio
    """
    x1, y1, x2, y2 = search_rect
    h, w = img.shape[:2]
    max_ratio = 0
    max_rect = (x1, y1, x1+box_size, y1+box_size)
    for cy in range(y1, y2-box_size+1):
        for cx in range(x1, x2-box_size+1):
            if cx < 0 or cy < 0 or cx+box_size > w or cy+box_size > h:
                continue
            roi = img[cy:cy+box_size, cx:cx+box_size]
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([160, 100, 100])
            upper_red2 = np.array([180, 255, 255])
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask = cv2.bitwise_or(mask1, mask2)
            ratio = cv2.countNonZero(mask) / (box_size * box_size)
            if ratio > max_ratio:
                max_ratio = ratio
                max_rect = (cx, cy, cx+box_size, cy+box_size)
    return max_rect, max_ratio

def is_color_match(img, x1, y1, x2, y2, target_color, tolerance=15):
    roi = img[y1:y2, x1:x2]
    avg_color = cv2.mean(roi)[:3]
    avg_color = np.round(avg_color).astype(int)
    target_bgr = target_color[::-1]
    diff = np.abs(avg_color - target_bgr)
    return np.all(diff <= tolerance)

def is_blue_target(img, roi, color_list, tolerance=8):
    x1, y1, x2, y2 = roi
    roi_img = img[y1:y2, x1:x2]
    avg_color = cv2.mean(roi_img)[:3]
    avg_color = np.round(avg_color).astype(int)
    for color in color_list:
        target_bgr = color[::-1]
        diff = np.abs(avg_color - target_bgr)
        if np.all(diff <= tolerance):
            print(f"检测到目标蓝绿色：{color}，实际={avg_color[::-1]}")
            return True
    return False

def region_has_color(img, center, color_list, offset=2, tolerance=20, ratio=0.5):
    x, y = center
    h, w = img.shape[:2]
    match_cnt = 0
    total_cnt = 0
    for dx in range(-offset, offset + 1):
        for dy in range(-offset, offset + 1):
            cx, cy = x + dx, y + dy
            if 0 <= cx < w and 0 <= cy < h:
                total_cnt += 1
                pixel = img[cy, cx]  # BGR
                for color in color_list:
                    bgr_color = color[::-1]
                    if np.all(np.abs(pixel - bgr_color) <= tolerance):
                        match_cnt += 1
                        break
    if total_cnt == 0:
        return False
    proportion = match_cnt / total_cnt
    return proportion >= ratio

def region_rect_major_color(img, rect, color_list, tolerance=20, ratio=0.5):
    x1, y1, x2, y2 = rect
    roi = img[y1:y2, x1:x2]
    # cv2.imshow('window title',roi)
    h, w = roi.shape[:2]
    match_cnt = 0
    total_cnt = h * w
    for yy in range(h):
        for xx in range(w):
            pixel = roi[yy, xx]  # BGR
            for color in color_list:
                bgr_color = color[::-1]
                if np.all(np.abs(pixel - bgr_color) <= tolerance):
                    match_cnt += 1
                    break
    if total_cnt == 0:
        return False
    proportion = match_cnt / total_cnt
    return proportion >= ratio
