# auto_fish

**星痕共鸣自动钓鱼工具**

本项目基于 [MAX_HYY](https://space.bilibili.com/189854873) 提供的 **自动钓鱼 1.3** 代码修改而来。

## 改动内容

- 使用 [mss](https://github.com/BoboTiG/python-mss) 替换 `pyautogui.screenshot`，以支持 **副显示器截图**。
- 使用 `ctypes.windll.shcore.SetProcessDpiAwareness(2)` 解决 **显示器 DPI 缩放** 问题。
- 增加红点区域的判定次数。
- 支持除 `1920×1080` 之外的其他 **16:9 分辨率**。
- 更改遛鱼逻辑
- 更改上钩逻辑
