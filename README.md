# auto_fish

**星痕共鸣自动钓鱼工具**

本项目基于 [MAX_HYY](https://space.bilibili.com/189854873) 提供的 **自动钓鱼 1.3** 代码修改而来。

## 改动内容

- 使用 [mss](https://github.com/BoboTiG/python-mss) 替换 `pyautogui.screenshot`，以支持 **副显示器截图**。
- 使用 `ctypes.windll.shcore.SetProcessDpiAwareness(2)`，以解决 **显示器 DPI 缩放** 问题。
