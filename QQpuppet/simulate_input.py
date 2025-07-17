import pyautogui
import time
import logging
import pyperclip

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('log/simulate_input_debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

def simulate_mouse_click(x, y, button='left'):
    # 移动鼠标到指定坐标并点击
    pyautogui.moveTo(x, y)
    if button == 'left':
        pyautogui.click()
    elif button == 'right':
        pyautogui.rightClick()

def simulate_scroll(amount):
    # 模拟滚轮滑动（正数向上，负数向下）
    pyautogui.scroll(amount)

def simulate_enter_key():
    # 模拟按下 Enter 键
    pyautogui.press('enter')

def simulate_keyboard_input(text, input_x, input_y):
    try:
        logger.debug(f"开始模拟键盘输入，目标坐标: ({input_x}, {input_y})")
        pyautogui.click(input_x, input_y)  # 点击输入框
        time.sleep(0.2)
        
        # 使用剪贴板输入中文
        pyperclip.copy(text)  # 将文本复制到剪贴板
        logger.debug(f"已将文本复制到剪贴板: {text}")
        pyautogui.hotkey('ctrl', 'v')  # 粘贴文本
        logger.debug("执行 Ctrl+V 粘贴")
        time.sleep(0.1)
    except Exception as e:
        logger.error(f"键盘输入失败: {str(e)}")

if __name__ == "__main__":
    # 示例：点击发送按钮
    button_x, button_y = 720,766  # 替换为 find_ui_element 的结果
    
    time.sleep(1)
    # simulate_mouse_click(button_x, button_y, 'left')
    # 示例：滚轮向下滚动
    pyautogui.moveTo(220,266)
    # simulate_scroll(-100)
    text = "过程装备腐蚀失效与防护（罗..."
    simulate_keyboard_input(text, 680,666)
    # 示例：复制并粘贴文本
    # simulate_copy_paste("Hello, this is a test message!")