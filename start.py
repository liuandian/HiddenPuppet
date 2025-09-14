import wxpuppet.execute_one as wx_start
import QQpuppet.start as qq_start
import QQpuppet.get_qq_window as get_qq_window
import wxpuppet.get_wx_window as get_wx_window
import QQpuppet.process_text as qq_process_text
import wxpuppet.process_text as wx_process_text
import time
import argparse

def qq_fetch_and_process_messages():
    """
    获取并处理消息内容
    """
    msgs = qq_process_text.fetch_posts_from_server()
    if isinstance(msgs, dict):
        # 假设消息内容在'result'字段中，参考之前的接口返回格式
        return msgs.get('result', '').strip()
    elif isinstance(msgs, str):
        return msgs.strip()
    else:
        print("获取消息时发生错误:", msgs.get('error'))
        return ""

def wx_fetch_and_process_messages():
    """
    获取并处理微信消息内容
    """
    msgs = wx_process_text.fetch_posts_from_server()
    if isinstance(msgs, dict):
        # 假设消息内容在'result'字段中，参考之前的接口返回格式
        return msgs.get('result', '').strip()
    elif isinstance(msgs, str):
        return msgs.strip()
    else:
        print("获取微信消息时发生错误:", msgs.get('error'))
        return ""

def wx_tai_fetch_and_process_messages():
    """
    获取泰yeah啦并处理微信消息内容
    """
    msgs = wx_process_text.fetch_tai_posts_from_server()
    if isinstance(msgs, dict):
        # 假设消息内容在'result'字段中，参考之前的接口返回格式
        return msgs.get('result', '').strip()
    elif isinstance(msgs, str):
        return msgs.strip()
    else:
        print("获取微信消息时发生错误:", msgs.get('error'))
        return ""

def run_scheduled(interval_minutes, test):
    """定时执行自动化任务，仅当有消息时才发送"""
    run_count = 0
    try:
        while True:
            print(f"\n=== 开始第 {run_count+1} 次执行检查 ===")

            # 先获取消息并检查是否为空
            qq_msg = qq_fetch_and_process_messages()
            wx_msg = wx_fetch_and_process_messages()
            wx_tai_msg = wx_tai_fetch_and_process_messages()
            
            if test:
                wx_msg = "【测试模式】" + (wx_msg if wx_msg else "无新消息")
                qq_start.automate_miniprogram(msg_content=qq_msg,test=True)
                wx_start.execute_one(page_num=3, msg_content=wx_msg, test=True)
                wx_start.execute_tai_one(page_num=1, msg_content=wx_tai_msg, test=True)
            else:
                #如果消息为空，直接返回不执行后续操作
                if not qq_msg and not wx_msg:
                    print("未获取到有效消息，本次不执行发送操作")
                
                if qq_msg:
                    print(f"QQ获取到有效消息，开始执行发送操作：\n{qq_msg}")
                    qq_start.automate_miniprogram(msg_content=qq_msg,test=False)
                if wx_msg:
                    print(f"微信获取到有效消息，开始执行发送操作：\n{wx_msg}")
                    wx_start.execute_one(page_num=3, msg_content=wx_msg, test=False)

            run_count += 1
                
            print(f"\n=== 第 {run_count} 次检查完成，等待 {interval_minutes} 分钟后再次检查 ===")
            time.sleep(interval_minutes * 60)  # 转换为秒
    
    except KeyboardInterrupt:
        print("\n程序被用户中断")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='微信小程序自动化转发工具（带消息检查）')
    parser.add_argument('-i', '--interval', type=int, default=20, help='执行间隔（分钟）')
    parser.add_argument('--no-test', dest='test', action='store_false', help='禁用测试模式')
    parser.set_defaults(test=True)  # 默认启用测试模式
    args = parser.parse_args()
    
    print(f"微信小程序自动化转发工具已启动，执行间隔: {args.interval} 分钟")
    print(f"测试模式: {'开启' if args.test else '关闭'}")
    get_qq_window.new_window_all()  # 读取QQ窗口位置
    get_wx_window.new_window_all()  # 读取微信窗口位置
        
    run_scheduled(args.interval, args.test)