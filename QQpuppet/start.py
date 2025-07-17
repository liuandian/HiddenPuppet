import test_find_ui
import simulate_input
import time
import process_text
import argparse
import get_qq_window
# 确保引入fetch_posts_from_server所在的模块
from process_text import fetch_posts_from_server  # 根据实际模块路径调整

def automate_miniprogram():
    # 先获取消息并检查是否为空
    msgs = fetch_posts_from_server()
    msg_content = ""
    
    # 解析消息内容（根据实际返回格式处理）
    if isinstance(msgs, dict):
        # 假设消息内容在'result'字段中，参考之前的接口返回格式
        msg_content = msgs.get('result', '').strip()
    elif isinstance(msgs, str):
        msg_content = msgs.strip()
    
    # 如果消息为空，直接返回不执行后续操作
    if not msg_content:
        print("未获取到有效消息，本次不执行发送操作")
        return
    
    print(f"获取到有效消息，开始执行发送操作：\n{msg_content}")
    
    # 消息非空时，执行后续自动化步骤
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
    
    # 查找“确认”按钮
    position = test_find_ui.find_final_send_element()
    if position:
        print(f"找到确认按钮，中心坐标: {position}")
        simulate_input.simulate_mouse_click(position[0], position[1], 'left')
        print("本次发送操作完成")
    else:
        print("未找到确认按钮，终止本次操作")
        return

def run_scheduled(interval_minutes, max_runs=None):
    """定时执行自动化任务，仅当有消息时才发送"""
    run_count = 0
    try:
        while max_runs is None or run_count < max_runs:
            print(f"\n=== 开始第 {run_count+1} 次执行检查 ===")
            # 直接调用automate_miniprogram，内部已包含消息检查逻辑
            automate_miniprogram()
            run_count += 1
            
            if max_runs is not None and run_count >= max_runs:
                print("已达到最大执行次数，程序退出")
                break
                
            print(f"\n=== 第 {run_count} 次检查完成，等待 {interval_minutes} 分钟后再次检查 ===")
            time.sleep(interval_minutes * 60)  # 转换为秒
    
    except KeyboardInterrupt:
        print("\n程序被用户中断")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='微信小程序自动化转发工具（带消息检查）')
    parser.add_argument('--interval', type=int, default=30, help='执行间隔（分钟）')
    parser.add_argument('--max-runs', type=int, default=None, help='最大执行次数')
    
    args = parser.parse_args()
    
    print(f"微信小程序自动化转发工具已启动，执行间隔: {args.interval} 分钟")
    get_qq_window.new_window_all()  # 读取QQ窗口位置
    
    if args.max_runs:
        print(f"最大执行次数: {args.max_runs}")
        
    run_scheduled(args.interval, args.max_runs)