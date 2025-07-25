# window_util.py

from datetime import datetime
import win32gui
import win32con
import win32process
import pyautogui
import ctypes
import os
import cv2
import numpy as np
import utils
import mss

from config import *

def find_window_by_process_name(process_name):
    hwnds = []
    def enum_window_callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                import psutil
                proc = psutil.Process(pid)
                if proc.name().lower() == process_name.lower():
                    hwnds.append(hwnd)
            except Exception:
                pass
    win32gui.EnumWindows(enum_window_callback, None)
    return hwnds

def get_window_rect(hwnd):
    return win32gui.GetWindowRect(hwnd)

def get_client_rect(hwnd):
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    # 转换为屏幕坐标（客户区左上、右下的屏幕绝对坐标）
    left_top = win32gui.ClientToScreen(hwnd, (left, top))
    right_bottom = win32gui.ClientToScreen(hwnd, (right, bottom))
    return (left_top[0], left_top[1], right_bottom[0], right_bottom[1])

def capture_window(hwnd):
    try:
        # 只截客户区，不含边框和标题栏
        x1, y1, x2, y2 = get_client_rect(hwnd)
        width = x2 - x1
        height = y2 - y1
        with mss.mss() as sct:
            monitor = {"left": x1, "top": y1, "width": width, "height": height}
            sct_img = sct.grab(monitor)
            img = np.array(sct_img)# [:, :, :3]  # 去掉 alpha 通道
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img
        # return img
        # print(f'client: width = {width},height = {height}')
        # screenshot = pyautogui.screenshot(region=(x1, y1, width, height))
        # print(f"已截取窗口客户区截图: {x1},{y1} - {x2},{y2} (宽度: {width}, 高度: {height})")
        # img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        # utils.save_screenshot(img, f'save_screen shot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        return img
    except Exception as e:
        print(f"截图失败: {e}")
        return None

def press_mouse_window(hwnd, rel_x, rel_y):
    # 基于客户区左上角的相对坐标
    client_rect = get_client_rect(hwnd)
    abs_x = client_rect[0] + rel_x
    abs_y = client_rect[1] + rel_y
    ctypes.windll.user32.SetCursorPos(abs_x, abs_y)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    print(f"鼠标左键已按下（窗口内: {rel_x},{rel_y} | 屏幕: {abs_x},{abs_y}）")

def release_mouse():
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    print("鼠标左键已释放")

def click_mouse_window(hwnd, rel_x, rel_y):
    # 基于客户区左上角的相对坐标
    client_rect = get_client_rect(hwnd)
    abs_x = client_rect[0] + rel_x
    abs_y = client_rect[1] + rel_y
    ctypes.windll.user32.SetCursorPos(abs_x, abs_y)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    import time
    time.sleep(0.01)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    print(f"鼠标左键单击完成（窗口内: {rel_x},{rel_y} | 屏幕: {abs_x},{abs_y}）")

def get_search_region(center, offset):
    """
    根据中心点和偏移量计算搜索矩形区域。
    :param center: (x, y) 搜索区域中心坐标
    :param offset: int 搜索区域半径（像素）
    :return: (left, top, right, bottom)
    """
    return (
        center[0] - offset,
        center[1] - offset,
        center[0] + offset,
        center[1] + offset
    )

def get_scale_area(rect, cur_w, cur_h, base_w=1920, base_h=1080):
    x1, y1, x2, y2 = rect
    scale_x = cur_w / base_w
    scale_y = cur_h / base_h
    return (
        int(x1 * scale_x),
        int(y1 * scale_y),
        int(x2 * scale_x),
        int(y2 * scale_y)
    )

def get_scale_point(point, cur_w, cur_h, base_w=1920, base_h=1080):
    x, y = point
    scale_x = cur_w / base_w
    scale_y = cur_h / base_h
    return int(x * scale_x), int(y * scale_y)