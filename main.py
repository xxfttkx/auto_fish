"""
作者: d233hj
创建日期: <2025-07-28  00:37:11>
最后编辑时间: <2025-08-02  01:32:30>
最后编辑人员: d233hj
FilePath: \auto_fish-main\main.py
"""

# main.py
import ctypes

ctypes.windll.shcore.SetProcessDpiAwareness(2)
import sys

sys.stdout.reconfigure(encoding="utf-8")
import time
import keyboard
from config import *
from window_util import *
from color_util import *
from utils import save_screenshot


def monitor_window(hwnd):
    isRunning = True
    last_key = [None]  # 记录上一次长按的"a"或"d"
    window = get_window_by_hwnd(hwnd)
    if not window:
        log(f"未找到窗口句柄 {hwnd} 对应的窗口")
        return

    def on_esc_press(e):
        if e.event_type == keyboard.KEY_DOWN and e.name == "esc":
            log("\n检测到 Esc 键按下，程序即将退出...")
            isRunning = False

    keyboard.on_press(on_esc_press)
    log("程序已启动，按 Esc 键可随时退出")
    window.activate()
    log("已切换到目标窗口")
    time.sleep(1)

    try:
        while isRunning:
            full_img = capture_window(hwnd)
            click_mouse_window(
                hwnd, *get_scale_point(CLICK_POS, full_img.shape[1], full_img.shape[0])
            )
            log(f"甩钩，{START_DELAY}秒后检测红点")

            # 新增：等待1秒检测特殊颜色区域
            time.sleep(2.5)
            full_img = capture_window(hwnd)
            height, width = full_img.shape[:2]
            # cv2.imshow('window title',full_img)
            if full_img is not None:
                found_post_cast = region_rect_major_color(
                    full_img,
                    get_scale_area(POST_CAST_CHECK_RECT, width, height),
                    POST_CAST_COLORS,
                    tolerance=POST_CAST_TOLERANCE,
                    ratio=POST_CAST_RATIO,
                )
                if found_post_cast:
                    log("鱼竿没耐久了，换杆")
                    # 第一步：模拟按下M键
                    keyboard.press(ROD_NO_DURABILITY_KEY)
                    time.sleep(0.05)
                    keyboard.release(ROD_NO_DURABILITY_KEY)
                    time.sleep(ROD_NO_DURABILITY_DELAY)
                    # 第二步：点击 ROD_CHANGE_CLICK_POS
                    window.activate()
                    click_mouse_window(hwnd, *ROD_CHANGE_CLICK_POS)
                    time.sleep(ROD_NO_DURABILITY_DELAY)
                    # 第三步：点击 ROD_CONFIRM_CLICK_POS
                    window.activate()
                    click_mouse_window(hwnd, *ROD_CONFIRM_CLICK_POS)
                    time.sleep(ROD_NO_DURABILITY_DELAY)
                    continue

            # 补足剩余延迟（如后面还需等到2秒），兼容原蓝色检测逻辑
            time.sleep(1)
            delay_start = time.time()
            blue_detected = False
            while time.time() - delay_start < (START_DELAY - 2):
                full_img = capture_window(hwnd)
                if full_img is not None:
                    if is_blue_target(
                        full_img,
                        get_scale_area(BLUE_ROI, width, height),
                        BLUE_COLORS,
                        tolerance=BLUE_TOLERANCE,
                    ):
                        log("鱼跑了")
                        blue_detected = True
                        break
                time.sleep(0.05)
            if blue_detected:
                continue

            # ====== 步骤2：自动定位红点密集区域 ======
            full_img = capture_window(hwnd)
            found_red = False
            count = 0
            while not found_red and count < 5:
                offset = count * 100  # 每次偏移100像素
                center = (
                    RED_SEARCH_REGION_CENTER[0],
                    RED_SEARCH_REGION_CENTER[1] + offset,
                )
                red_rect, red_ratio = find_max_red_region(
                    full_img,
                    get_search_region(
                        get_scale_point(center, width, height), RED_SEARCH_REGION_OFFSET
                    ),
                    RED_DETECT_BOX_SIZE,
                    RED_THRESHOLD,
                )
                # utils.save_screenshot(full_img, f'full_img')
                log(f"检测到红点区域：{red_rect}, 密集度={red_ratio:.2f}")
                count += 1
                if red_ratio >= RED_THRESHOLD:
                    break
            if red_ratio < RED_THRESHOLD:
                log("找不到红点")
                return

            red_start_time = None
            is_pressed = False
            cycle_active = True
            blue_check_enable = True

            while cycle_active and isRunning:
                full_img = capture_window(hwnd)
                if full_img is None:
                    time.sleep(0.1)
                    continue

                if blue_check_enable and is_blue_target(
                    full_img,
                    get_scale_area(BLUE_ROI, width, height),
                    BLUE_COLORS,
                    tolerance=BLUE_TOLERANCE,
                ):
                    log("鱼跑了")
                    break

                # 只监控本轮刚刚自动检测到的红点区域
                x1, y1, x2, y2 = red_rect
                roi = full_img[y1:y2, x1:x2]
                red = is_red_dominant(roi, threshold=RED_THRESHOLD)

                if CAPTURE_SCREENSHOT:
                    save_screenshot(full_img, "red_zone")

                if not red:
                    if red_start_time is None:
                        red_start_time = time.time()
                    elif time.time() - red_start_time > RED_NOT_FOUND_TIME:
                        if not is_pressed:
                            log(
                                "红点消失超过{:.1f}秒，上钩了".format(
                                    RED_NOT_FOUND_TIME
                                )
                            )
                            press_mouse_window(hwnd, *CLICK_POS)
                            is_pressed = True
                else:
                    red_start_time = None

                # ------- A/D互斥长按逻辑 -------
                if is_pressed:
                    found_a = region_has_color(
                        full_img,
                        get_scale_point(POINT_A_POS, width, height),
                        POINT_CHECK_COLORS,
                        offset=POINT_REGION_OFFSET,
                        tolerance=POINT_CHECK_TOLERANCE,
                        ratio=POINT_REGION_RATIO,
                    )
                    found_d = region_has_color(
                        full_img,
                        get_scale_point(POINT_D_POS, width, height),
                        POINT_CHECK_COLORS,
                        offset=POINT_REGION_OFFSET,
                        tolerance=POINT_CHECK_TOLERANCE,
                        ratio=POINT_REGION_RATIO,
                    )
                    target_key = None
                    if found_a:
                        target_key = "a"
                    elif found_d:
                        target_key = "d"
                    if target_key and target_key != last_key[0]:
                        if last_key[0] == "a":
                            keyboard.release("a")
                        elif last_key[0] == "d":
                            keyboard.release("d")
                        keyboard.press(target_key)
                        last_key[0] = target_key

                    cx1, cy1, cx2, cy2 = get_scale_area(COLOR_CHECK_AREA, width, height)
                    if is_color_match(full_img, cx1, cy1, cx2, cy2, TARGET_COLOR):
                        log(f"钓鱼完成")
                        release_mouse()
                        is_pressed = False
                        blue_check_enable = False
                        # ===== 这里是新加的配置延迟 =====
                        time.sleep(AFTER_DETECT_CLICK_DELAY)
                        click_mouse_window(
                            hwnd, *(get_scale_point(SECOND_CLICK_POS, width, height))
                        )
                        log(f"{AFTER_SECOND_CLICK_DELAY}秒后继续钓鱼")
                        time.sleep(AFTER_SECOND_CLICK_DELAY)
                        cycle_active = False
                        if last_key[0] == "a":
                            keyboard.release("a")
                        if last_key[0] == "d":
                            keyboard.release("d")
                        last_key[0] = None
                else:
                    if last_key[0] == "a":
                        keyboard.release("a")
                        last_key[0] = None
                    if last_key[0] == "d":
                        keyboard.release("d")
                        last_key[0] = None

                time.sleep(0.01)
    except Exception as e:
        log("发生异常：", e)
    finally:
        release_mouse()
        if last_key[0] == "a":
            keyboard.release("a")
        if last_key[0] == "d":
            keyboard.release("d")
        keyboard.unhook_all()
        log("程序已终止。")


if __name__ == "__main__":
    hwnds = find_window_by_process_name(PROCESS_NAME)
    if not hwnds:
        log(f"未找到名为 {PROCESS_NAME} 的窗口")
    else:
        hwnd = hwnds[0]
        log("开始监控窗口：", win32gui.GetWindowText(hwnd))
        monitor_window(hwnd)
