import QQpuppet.test_find_ui as test_find_ui
import QQpuppet.simulate_input as simulate_input
import time
import QQpuppet.process_text as process_text
import argparse
import QQpuppet.get_qq_window as get_qq_window
# 确保引入fetch_posts_from_server所在的模块
from QQpuppet.process_text import fetch_posts_from_server  # 根据实际模块路径调整

def automate_miniprogram(msg_content=None,test=True):

    # 查找小程序（需提前保存发送按钮的模板图像）
    position = test_find_ui.find_miniprogram_element()
    if position:
        print(f"找到小程序，中心坐标: {position}")
        simulate_input.simulate_mouse_click(position[0], position[1], 'right')
    else:
        print("未找到小程序元素，终止本次操作")
        return  # 关键步骤失败，终止本次执行
    
    # 查找“转发”按钮（需提前保存转发按钮的模板图像）
    position = test_find_ui.find_forward_button_element()
    if position:
        print(f"找到转发按钮，中心坐标: {position}")
        simulate_input.simulate_mouse_click(position[0], position[1], 'left')
    else:
        print("未找到转发按钮，终止本次操作")
        return
    
    # 查找“搜索群聊”按钮
    position = test_find_ui.find_search_group_button_element()
    if position:
        print(f"找到搜索群聊按钮，中心坐标: {position}")
        time.sleep(0.1)
        simulate_input.simulate_keyboard_input("小竹校友圈", position[0], position[1])
    else:
        print("未找到搜索群聊按钮，终止本次操作")
        return
    
    # 查找搜索结果并选择
    matches = test_find_ui.find_multi_group_button_element()
    if matches:
        for match in matches:
            print(f"找到群聊按钮，中心坐标: {match}")
            simulate_input.simulate_mouse_click(match[0], match[1], 'left')
            time.sleep(0.1)
    else:
        print("未找到群聊按钮，终止本次操作")
        return
    
    # 查找“留言”按钮并输入（使用前面获取的消息）
    position = test_find_ui.find_send_msg_element()
    if position:
        print(f"找到留言按钮，中心坐标: {position}")
        simulate_input.simulate_mouse_click(position[0], position[1], 'left')
        # 直接使用前面获取的msg_content，无需再次调用process_text
        simulate_input.simulate_keyboard_input(msg_content, position[0], position[1])
    else:
        print("未找到留言按钮，终止本次操作")
        return
    
    if test:
        # 查找“取消”按钮
        position = test_find_ui.find_cancel_button_element()
        if position:
            print(f"找到取消按钮，中心坐标: {position}")
            simulate_input.simulate_mouse_click(position[0], position[1], 'left')
        else:
            print("未找到取消按钮")
    else:
        # 查找“确认”按钮
        position = test_find_ui.find_final_send_element()
        if position:
            print(f"找到发送按钮，中心坐标: {position}")
            simulate_input.simulate_mouse_click(position[0], position[1], 'left')
        else:
            print("未找到发送按钮")


if __name__ == "__main__":
    automate_miniprogram(msg_content="msg", test=True)  # 替换为实际消息内容