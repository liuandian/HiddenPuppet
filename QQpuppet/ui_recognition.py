import test_find_ui
import simulate_input
import time
import process_text


if __name__ == "__main__":

    # 查找小程序（需提前保存发送按钮的模板图像）
    position = test_find_ui.find_miniprogram_element()
    if position:
        print(f"找到小程序，中心坐标: {position}")
        simulate_input.simulate_mouse_click(position[0], position[1], 'right')
    else:
        print("未找到发送按钮")
    
    # 查找“转发”按钮（需提前保存转发按钮的模板图像）
    position = test_find_ui.find_forward_button_element()
    if position:
        print(f"找到发送按钮，中心坐标: {position}")
        simulate_input.simulate_mouse_click(position[0], position[1], 'left')
    else:
        print("未找到发送按钮")
        
    # 查找“搜索群聊”按钮（需提前保存转发按钮的模板图像）
    position = test_find_ui.find_search_group_button_element()
    if position:
        print(f"找到发送按钮，中心坐标: {position}")
        # simulate_input.simulate_mouse_click(position[0], position[1], 'left')
        time.sleep(0.1)
        simulate_input.simulate_keyboard_input("小竹校友圈", position[0], position[1])
    else:
        print("未找到发送按钮")
        
        
    # 查找搜索结果并选择
    matches = test_find_ui.find_multi_group_button_element()
    if matches:
        # simulate_input.simulate_mouse_click(position[0], position[1], 'left')
        for match in matches:
            print(f"找到群聊按钮，中心坐标: {match}")
            simulate_input.simulate_mouse_click(match[0], match[1], 'left')
            time.sleep(0.1)
    else:
        print("未找到群聊按钮")
    
    
    # 查找“留言”按钮并输入
    position = test_find_ui.find_send_msg_element()
    if position:
        print(f"找到留言按钮，中心坐标: {position}")
        simulate_input.simulate_mouse_click(position[0], position[1], 'left')
        msg = process_text.process_posts()
        simulate_input.simulate_keyboard_input(msg, position[0], position[1])
    else:
        print("未找到留言按钮")
        
        
    # 查找“确认”按钮
    position = test_find_ui.find_final_send_element()
    if position:
        print(f"找到发送按钮，中心坐标: {position}")
        simulate_input.simulate_mouse_click(position[0], position[1], 'left')
    else:
        print("未找到发送按钮")