import wxpuppet.test_find_ui as test_find_ui
import wxpuppet.simulate_input as simulate_input
import wxpuppet.get_wx_window as get_wx_window
import time
import wxpuppet.process_text as process_text

def execute_one(page_num=1,msg_content=None,test = True):
    
    
    # 查找初始搜索框（需提前保存发送按钮的模板图像）
    position = test_find_ui.find_first_search()
    if position:
        print(f"找到初始搜索框，中心坐标: {position}")
        time.sleep(0.1)
        simulate_input.simulate_keyboard_input(f"xzxyq3", position[0], position[1])
    else:
        print("未找到初始搜索框")
        return
    
    # 查找自己对话框按钮
    position = test_find_ui.find_first_self()
    if position:
        print(f"找到自己对话框，中心坐标: {position}")
        simulate_input.simulate_mouse_click(position[0], position[1], 'left')
        
    else:
        print("未找到自己对话框")    
        return    
    

    # 查找输入框按钮
    position = test_find_ui.find_input_box()
    if position:
        print(f"找到输入框，中心坐标: {position}")
        simulate_input.simulate_mouse_click(position[0], position[1], 'left')
        time.sleep(0.1)
        simulate_input.simulate_keyboard_input(msg_content, position[0], position[1])
    
    else:
        print("未找到输入框")   
        return   
    
    
    # 查找输入框消息发送按钮
    position = test_find_ui.find_input_send_button()
    if position:
        print(f"找到输入框消息发送按钮，中心坐标: {position}")
        simulate_input.simulate_mouse_click(position[0], position[1], 'left')
        
    else:
        print("未找到输入框消息发送按钮") 
        return
        
        
               
    for i in range(page_num):
        
        # 查找唯一被发送消息
        position = test_find_ui.find_uni_sended_msg_element()
        if position:
            print(f"找到唯一被发送消息，中心坐标: {position}")
            simulate_input.simulate_mouse_click(position[0]-50, position[1], 'right')
            
        else:
            print("未找到唯一被发送消息")
            return          
        
        
        # 查找“转发”按钮（需提前保存转发按钮的模板图像）
        position = test_find_ui.find_forward_button_element()
        if position:
            print(f"找到转发按钮，中心坐标: {position}")
            simulate_input.simulate_mouse_click(position[0], position[1], 'left')
        else:
            print("未找到转发按钮")
            return
            
        # 查找“搜索群聊”按钮（需提前保存转发按钮的模板图像）
        position = test_find_ui.find_search_group_button_element()
        if position:
            print(f"找到搜索群聊按钮，中心坐标: {position}")
            # simulate_input.simulate_mouse_click(position[0], position[1], 'left')
            time.sleep(0.1)
            simulate_input.simulate_keyboard_input(f"小竹校友圈{i}", position[0], position[1])
        else:
            print("未找到搜索群聊按钮")
            return
            
        
        # 查找“展开所有”按钮
        position = test_find_ui.find_show_all_group_element()
        if position:
            print(f"找到展开所有按钮，中心坐标: {position}")
            simulate_input.simulate_mouse_click(position[0], position[1], 'left')
            time.sleep(0.1)
            
            # 有展开时先点一次
            matches = test_find_ui.find_multi_group_button_element()
            if matches:
                # simulate_input.simulate_mouse_click(position[0], position[1], 'left')
                for match in matches:
                    print(f"找到群聊按钮，中心坐标: {match}")
                    simulate_input.simulate_mouse_click(match[0], match[1], 'left')
                    time.sleep(0.1)
            else:
                print("未找到群聊按钮")
            
            simulate_input.simulate_scroll(-400)
            
            
        else:
            print("未找到展开所有按钮")
        


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
            
                    
        # # 查找“留言”按钮并输入
        # position = test_find_ui.find_send_msg_element()
        # if position:
        #     print(f"找到留言按钮，中心坐标: {position}")
        #     simulate_input.simulate_mouse_click(position[0], position[1], 'left')
        #     simulate_input.simulate_keyboard_input(msg_content, position[0], position[1])
        # else:
        #     print("未找到留言按钮")
        
        if test:
            # # 查找“取消”按钮
            position = test_find_ui.find_cancel_button_element()
            if position:
                print(f"找到取消按钮，中心坐标: {position}")
                simulate_input.simulate_mouse_click(position[0], position[1], 'left')
            else:    
                print("未找到取消按钮")
                return
        else:
            # 查找“确认”按钮
            position = test_find_ui.find_final_send_element()
            if position:
                print(f"找到发送按钮，中心坐标: {position}")
                simulate_input.simulate_mouse_click(position[0], position[1], 'left')
            else:
                print("未找到分别发送按钮，尝试单独发送")
                position = test_find_ui.find_send_button_element()
                if position:
                    print(f"找到发送按钮，中心坐标: {position}")
                    simulate_input.simulate_mouse_click(position[0], position[1], 'left')
                else:
                    print("未找到确认按钮")
                    return  
  

if __name__ == "__main__":
    execute_one(page_num=3, msg_content="msg",test = True)  # 替换为实际消息内容

