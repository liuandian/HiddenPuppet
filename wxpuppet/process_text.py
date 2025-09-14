from typing import List
import requests
from threading import Timer
import time


def fetch_posts_from_server():
    """
    从远程服务器获取帖子数据
    """
    url = 'https://www.scuclub.top/api/blog/fetchPosts/'  # 根据实际情况更新 URL
    try:
        response = requests.get(url)
        response.raise_for_status()  # 如果请求失败，抛出 HTTPError 异常
        print("拿到消息：",response.json())
        return response.json()  # 解析 JSON 响应
    except requests.RequestException as e:
        # 捕获并处理请求异常
        return {'error': str(e)}

def fetch_tai_posts_from_server():
    """
    从远程服务器获取泰yeah啦帖子数据
    """
    url = 'https://www.scuclub.top/api/blog/fetchTaiPosts/'  # 根据实际情况更新 URL
    try:
        response = requests.get(url)
        response.raise_for_status()  # 如果请求失败，抛出 HTTPError 异常
        print("拿到消息：",response.json())
        return response.json()  # 解析 JSON 响应
    except requests.RequestException as e:
        # 捕获并处理请求异常
        return {'error': str(e)}
        
def process_posts():
    """
    获取帖子数据并处理
    """
    msgs = fetch_posts_from_server()
    if isinstance(msgs, dict):
        if 'error' in msgs:
            print("获取帖子数据时发生错误:", msgs['error'])
        else:
            result_message = msgs.get('result', '')
            # print(result_message)
            return result_message
    else:
        print("获取帖子数据时发生错误:", msgs.get('error'))



if __name__ == "__main__":
    msg = process_posts()
    print(msg)
