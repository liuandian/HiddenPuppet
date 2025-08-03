import win32gui
import win32con
import pyautogui
import cv2
import numpy as np
import logging
import os
import time
import json


# 创建 log 和 cache 文件夹
os.makedirs("wxpuppet/log", exist_ok=True)
os.makedirs("wxpuppet/cache", exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wxpuppet/log/wx_window_debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

def find_wx_window():
    logger.debug("开始查找 wx 窗口")
    hwnd = win32gui.FindWindow(None, None)
    while hwnd:
        window_title = win32gui.GetWindowText(hwnd)
        if "微信" in window_title:
            # 获取窗口位置和大小
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            logger.debug(f"找到窗口: {window_title}, 位置: ({left}, {top}, {right}, {bottom})")
            if win32gui.IsWindowVisible(hwnd) and not win32gui.IsIconic(hwnd):
                logger.info(f"找到可见的 wx 窗口: {window_title}")
                return hwnd, (left, top, right, bottom)
            else:
                logger.debug(f"窗口 {window_title} 不可见或最小化")
        hwnd = win32gui.GetWindow(hwnd, win32con.GW_HWNDNEXT)
    logger.warning("未找到任何 wx 窗口")
    return None, None

def capture_wx_window(left, top, right, bottom, output_path="wxpuppet/cache/wx_window_screenshot.png"):
    try:
        logger.debug(f"开始捕获窗口截图，区域: ({left}, {top}, {right-left}, {bottom-top})")
        time.sleep(0.5)  # 短暂延迟以确保窗口准备好
        screenshot = pyautogui.screenshot(region=(left, top, right-left, bottom-top))
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_path, screenshot)
        logger.info(f"截图已保存至: {output_path}")
        return screenshot
    except Exception as e:
        logger.error(f"截图失败: {str(e)}")
        return None

def save_window_position(left, top, right, bottom, output_path="wxpuppet/cache/window_position.json"):
    try:
        logger.debug(f"保存窗口位置到: {output_path}")
        position = {
            "left": left,
            "top": top,
            "right": right,
            "bottom": bottom
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(position, f, ensure_ascii=False, indent=4)
        logger.info(f"窗口位置已保存至: {output_path}")
    except Exception as e:
        logger.error(f"保存窗口位置失败: {str(e)}")

def read_window_position(input_path="wxpuppet/cache/window_position.json"):
    try:
        logger.debug(f"开始读取窗口位置从: {input_path}")
        if not os.path.exists(input_path):
            logger.error(f"位置文件 {input_path} 不存在")
            return None
        
        with open(input_path, 'r', encoding='utf-8') as f:
            position = json.load(f)
        
        left = position.get("left")
        top = position.get("top")
        right = position.get("right")
        bottom = position.get("bottom")
        if all(isinstance(x, int) for x in [left, top, right, bottom]) and right > left and bottom > top:
            logger.info(f"成功读取窗口位置: 左上角 ({left}, {top}), 右下角 ({right}, {bottom})")
            return left, top, right, bottom
        else:
            logger.error(f"坐标无效: 左上角 ({left}, {top}), 右下角 ({right}, {bottom})")
            return None
    except Exception as e:
        logger.error(f"读取窗口位置失败: {str(e)}")
        return None

def new_window_all():
    try:
        hwnd, rect = find_wx_window()
        if hwnd:
            left, top, right, bottom = rect
            print(f"wx 窗口位置: 左上角 ({left}, {top}), 右下角 ({right}, {bottom})")
            logger.info(f"wx 窗口位置: 左上角 ({left}, {top}), 右下角 ({right}, {bottom})")
            
            # 保存窗口位置
            save_window_position(left, top, right, bottom)
            
            # 捕获窗口截图
            screenshot = capture_wx_window(left, top, right, bottom)
            if screenshot is not None:
                print(f"截图已保存至: wxpuppet/cache/wx_window_screenshot.png")
            else:
                print("截图失败，请检查日志")
        else:
            print("未找到 wx 窗口")
    except Exception as e:
        logger.exception(f"程序执行出错: {str(e)}")
        print(f"发生错误: {str(e)}")    

if __name__ == "__main__":
    new_window_all()
        
    read_window_position()