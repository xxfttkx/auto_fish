# window_util.py

from datetime import datetime
import win32gui
import win32process
import pygetwindow as gw
import ctypes
import cv2
import numpy as np
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
        # log(f'client: width = {width},height = {height}')
        # screenshot = pyautogui.screenshot(region=(x1, y1, width, height))
        # log(f"已截取窗口客户区截图: {x1},{y1} - {x2},{y2} (宽度: {width}, 高度: {height})")
        # img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        # utils.save_screenshot(img, f'save_screen shot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        return img
    except Exception as e:
        log(f"截图失败: {e}")
        return None

def press_mouse_window(hwnd, rel_x, rel_y):
    # 基于客户区左上角的相对坐标
    client_rect = get_client_rect(hwnd)
    abs_x = client_rect[0] + rel_x
    abs_y = client_rect[1] + rel_y
    ctypes.windll.user32.SetCursorPos(abs_x, abs_y)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    log(f"鼠标左键已按下（窗口内: {rel_x},{rel_y} | 屏幕: {abs_x},{abs_y}）")

def release_mouse():
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    log("鼠标左键已释放")

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
    log(f"鼠标左键单击完成（窗口内: {rel_x},{rel_y} | 屏幕: {abs_x},{abs_y}）")

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

def get_scale_val(val, cur_w, cur_h, base_w=1920, base_h=1080):
    scale_x = cur_w / base_w
    return val * scale_x

def get_int_scale_val(val, cur_w, cur_h, base_w=1920, base_h=1080):
    return int(get_scale_val(val, cur_w, cur_h, base_w, base_h))

def log(*args, sep=' ', end='\n'):
    """带时间前缀的打印函数，支持多个参数"""
    now = datetime.now().strftime("[%H:%M:%S]")
    print(now, *args, sep=sep, end=end)

def find_target_window():
    """查找并返回窗口标题完全是 '星痕共鸣' 的窗口对象"""
    all_windows = gw.getAllWindows()
    for w in all_windows:
        if w.title == "星痕共鸣":
            log("成功获取目标窗口")
            return w
    log("未找到游戏窗口")
    return None

def get_window_by_hwnd(hwnd):
    """根据窗口句柄获取窗口对象"""
    try:
        return gw.Window(hWnd=hwnd)
    except Exception as e:
        log(f"获取窗口失败: {e}")
        return None

def find_best_water_region(screenshot, fish_region, template_path, step=10):
    """
    在screenshot里，围绕fish_region中心点，横向滑动template宽度的矩形区域，y不变，找最佳匹配。

    参数:
        screenshot: np.array, BGR图
        fish_region: (x, y, w, h)
        template_path: 模板路径，灰度读入
        step: 横向滑动步长
        search_range: 滑动范围，单位像素，左右各search_range像素

    返回:
        best_rect: (x, y, w, h)
        best_score: 匹配得分
    """
    height, width = screenshot.shape[:2]
    step = get_int_scale_val(step, width, height)
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        raise FileNotFoundError(f"模板图像未找到: {template_path}")
    template_h, template_w = template.shape
    template_h = get_int_scale_val(template_h, width, height)
    template_w = get_int_scale_val(template_w, width, height)
    # 鱼区中心横坐标
    fish_center_x = fish_region[0] + fish_region[2] // 2
    # y坐标固定（可以用fish_region[1]或者更精细定位，比如中心纵坐标减去一半模板高）
    y = fish_region[1]

    # 先转成灰度图，方便matchTemplate
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    best_score = -1
    best_rect = None

    # 计算滑动范围的左右边界，保证不超出截图边界
    x_start = 0
    
    x_end = width

    for x in range(x_start, x_end + 1, step):
        # 拿 2 倍高度的区域
        multi = 2
        combined_region = screenshot_gray[y:y + multi * template_h, x:x + template_w]
        if combined_region.shape != (multi * template_h, template_w):
            continue

        white_mask = (combined_region > 210).astype(np.uint8)
        white_pixels = cv2.countNonZero(white_mask)
        total_pixels = combined_region.shape[0] * combined_region.shape[1]
        score = white_pixels / total_pixels

        if score > best_score:
            best_score = score
            best_rect = (x, y, template_w, 2 * template_h)
        

    # log(f"Best match: {best_rect}, score={best_score:.4f}")
    return best_rect, best_score
