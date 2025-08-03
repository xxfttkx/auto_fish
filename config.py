# config.py

# ====== 基本参数 ======
PROCESS_NAME = "Star.exe"             # 要自动化的进程名
LOG_DIR = "log"                       # 截图和日志保存目录
CAPTURE_SCREENSHOT = False            # 是否在每轮保存截图（调试用）

# ====== 操作坐标 ======
CLICK_POS = (922, 380)                # 甩钩/上钩时的点击位置（窗口内坐标）
SECOND_CLICK_POS = (1600, 1010)       # 钓鱼完成后点击的位置（窗口内坐标）

# ====== 红点检测参数 ======
# 红点大区域自动搜索（中心±offset范围），建议中心为鱼漂预期区，offset越大范围越大
RED_SEARCH_REGION_CENTER = (922, 383)            # 红点搜索区域中心
XuanYa = (922, 600)         # 红点搜索区域中心
RED_SEARCH_REGION_OFFSET = 100                # 搜索区域半径（像素）
RED_SEARCH_REGION_RECT = (                    # 红点大搜索区域(左上x,左上y,右下x,右下y)
    RED_SEARCH_REGION_CENTER[0] - RED_SEARCH_REGION_OFFSET,
    RED_SEARCH_REGION_CENTER[1] - RED_SEARCH_REGION_OFFSET,
    RED_SEARCH_REGION_CENTER[0] + RED_SEARCH_REGION_OFFSET,
    RED_SEARCH_REGION_CENTER[1] + RED_SEARCH_REGION_OFFSET
)
RED_DETECT_BOX_SIZE = 7             # 红点检测小方块边长（像素，建议7）
RED_THRESHOLD = 0.6                 # 判定红色像素比例的阈值
RED_NOT_FOUND_TIME = 0.7          # 红点消失多长时间判定为“上钩”（秒）

# ====== 钓鱼完成检测参数（灰色区域）======
COLOR_CHECK_AREA = (1454, 980, 1520, 1003)    # 判定钓鱼完成的灰色区域（窗口内坐标）
TARGET_COLOR = (232, 232, 232)                # 钓鱼完成时该区域应为的目标颜色（RGB）

# ====== 延迟参数 ======
START_DELAY = 5                    # 甩钩后启动延迟（秒）
AFTER_SECOND_CLICK_DELAY = 3       # 钓鱼完成后点击SECOND_CLICK_POS后的等待时间（秒）

# ====== 等级检测（鱼跑了检测）======
BLUE_ROI = (1178, 989, 1225, 1019) # 检测鱼跑了的蓝绿色区域（窗口内坐标）
BLUE_COLORS = [                    # 判定“鱼跑了”时的目标蓝绿色
    (41, 140, 149),
    (31, 117, 133),
    (31, 114, 131),
    (34, 119, 134),
    (36, 126, 139),
]
BLUE_TOLERANCE = 15                 # 颜色误差容忍度

# ====== 鼠标事件码 ======
MOUSEEVENTF_LEFTDOWN = 0x0002      # 鼠标左键按下事件码
MOUSEEVENTF_LEFTUP = 0x0004        # 鼠标左键抬起事件码

# ====== A/D按键判定参数 ======
POINT_A_POS = (938, 540)           # 检查“A”键的判定点（窗口内坐标）
POINT_D_POS = (982, 540)           # 检查“D”键的判定点（窗口内坐标）
POINT_CHECK_COLORS = [             # “A/D”判定目标颜色
    (216, 209, 196),
    (237, 243, 247),
    (219, 211, 197)
]
POINT_CHECK_TOLERANCE = 20         # “A/D”颜色容忍度
POINT_REGION_OFFSET = 2            # 检测区域范围(判定点±几像素)
POINT_REGION_RATIO = 0.5           # 检测区域内目标颜色占比判定阈值

# ====== 甩钩后耐久检测 ======
POST_CAST_CHECK_RECT = (1641, 1024, 1660, 1039)    # 甩钩后耐久检测区域
POST_CAST_COLORS = [                               # 鱼竿没耐久时该区域目标色
    (137, 145, 153),
    (131, 138, 145),
    (95, 101, 107),
    (95, 102, 107),
]
POST_CAST_TOLERANCE = 20                           # 颜色容忍度
POST_CAST_RATIO = 0.5                              # 匹配目标色像素比例阈值

# ====== 鱼竿没耐久时的处理参数 ======
ROD_NO_DURABILITY_KEY = "m"        # 鱼竿没耐久后按下的键
ROD_CHANGE_CLICK_POS = (1722, 595) # 更换鱼竿点击位置
ROD_CONFIRM_CLICK_POS = (750, 300) # 更换鱼竿后确认点击位置
ROD_NO_DURABILITY_DELAY = 1        # 每步操作之间的等待（秒）

# ====== 钓鱼完成后点击的延迟（秒）（新增，控制点击更快或更慢）======
AFTER_DETECT_CLICK_DELAY = 1    # 检测到钓鱼完成后到点击SECOND_CLICK_POS之间的延迟，越小越快
