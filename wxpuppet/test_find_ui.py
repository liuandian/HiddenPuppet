import cv2
import numpy as np
import logging
from PIL import Image
import pyautogui
import time
import os
import wxpuppet.get_wx_window as get_wx_window

# 创建 log 和 cache 文件夹
os.makedirs("wxpuppet/log", exist_ok=True)
os.makedirs("wxpuppet/cache", exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wxpuppet/log/ui_element_debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

def find_ui_element(template_path, threshold=0.7):
    logger.debug("开始执行 find_ui_element 函数")
    left, top, right, bottom = get_wx_window.read_window_position()
    region = (left, top, right-left, bottom-top)
    screenshot = capture_screenshot(region)  # 可传入 region=(left, top, width, height)
    
    # 检查模板图像是否存在
    if not os.path.exists(template_path):
        logger.error(f"模板图像 {template_path} 不存在")
        return None
    
    # 加载模板图像
    # logger.debug(f"加载模板图像: {template_path}")
    template = cv2.imread(template_path, 0)
    if template is None:
        logger.error(f"无法加载模板图像 {template_path}")
        return None
    
    # 记录模板图像尺寸
    template_h, template_w = template.shape
    # logger.debug(f"模板图像尺寸: {template_w}x{template_h}")
    
    # 检查截图是否有效
    if screenshot is None:
        logger.error("截图为空")
        return None
    
    # 记录截图尺寸
    screenshot_h, screenshot_w = screenshot.shape[:2]
    logger.debug(f"截图尺寸: {screenshot_w}x{screenshot_h}")
    
    # 转换为灰度图
    # logger.debug("将截图转换为灰度图")
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    
    # 执行模板匹配
    # logger.debug("执行模板匹配 (方法: TM_CCOEFF_NORMED)")
    result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
    
    # 获取匹配结果
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    logger.debug(f"匹配结果 - 最小值: {min_val:.4f}, 最大值: {max_val:.4f}")
    logger.debug(f"最大值位置 (top_left): {max_loc}")
    
    # 检查置信度
    if max_val >= threshold:
        logger.info(f"匹配成功，置信度: {max_val:.4f} (阈值: {threshold})")
        top_left = max_loc
        center_x = top_left[0] + template_w // 2
        center_y = top_left[1] + template_h // 2
        logger.debug(f"计算中心坐标: ({center_x}, {center_y})")
        
        # 可视化匹配结果
        logger.debug("生成匹配结果可视化图像")
        screenshot_with_box = screenshot.copy()
        bottom_right = (top_left[0] + template_w, top_left[1] + template_h)
        cv2.rectangle(screenshot_with_box, top_left, bottom_right, (0, 255, 0), 2)
        cv2.circle(screenshot_with_box, (center_x, center_y), 5, (0, 0, 255), -1)
        
        # 保存可视化结果
        output_path = "wxpuppet/cache/match_result.png"
        cv2.imwrite(output_path, screenshot_with_box)
        logger.info(f"匹配结果已保存至: {output_path}")
        
        return center_x, center_y
    else:
        logger.warning(f"匹配失败，置信度: {max_val:.4f} 小于阈值 {threshold}")
        # 保存原始截图以供调试
        output_path = "wxpuppet/cache/failed_screenshot.png"
        cv2.imwrite(output_path, screenshot)
        logger.info(f"未匹配成功的截图已保存至: {output_path}")
        return None

def create_mask(template, ignore_region=None):
    """创建掩码，忽略指定区域"""
    mask = np.ones(template.shape, dtype=np.uint8) * 255  # 默认全白（参与匹配）
    if ignore_region:
        x, y, w, h = ignore_region
        mask[y:y+h, x:x+w] = 0  # 忽略区域设为黑色
    logger.debug(f"创建掩码，忽略区域: {ignore_region}")
    output_path = "wxpuppet/cache/template_mask.png"
    cv2.imwrite(output_path, mask)
    logger.info(f"掩码已保存至: {output_path}")
    return mask

def calculate_iou(box1, box2):
    """计算两个框的 IoU"""
    x1_1, y1_1, x2_1, y2_1 = box1
    x1_2, y1_2, x2_2, y2_2 = box2
    
    x1_i = max(x1_1, x1_2)
    y1_i = max(y1_1, y1_2)
    x2_i = min(x2_1, x2_2)
    y2_i = min(y2_1, y2_2)
    
    intersection = max(0, x2_i - x1_i) * max(0, y2_i - y1_i)
    area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
    area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
    union = area1 + area2 - intersection
    
    iou = intersection / union if union > 0 else 0
    return iou

def non_max_suppression(locations, scores, template_w, template_h, iou_threshold=0.5):
    """非极大值抑制，基于 IoU 过滤重叠的匹配框"""
    logger.debug("开始执行 non_max_suppression")
    
    if len(locations) == 0 or len(scores) == 0:
        logger.debug("输入 locations 或 scores 为空")
        return [], []
    
    if len(locations) != len(scores):
        logger.error(f"locations ({len(locations)}) 和 scores ({len(scores)}) 长度不匹配")
        return [], []
    
    # 构造边界框并记录详细信息
    boxes = []
    for i, loc in enumerate(locations):
        x1, y1 = int(loc[0]), int(loc[1])  # 转换为整数
        x2, y2 = x1 + template_w, y1 + template_h
        boxes.append([x1, y1, x2, y2])
        center_x = x1 + template_w // 2
        center_y = y1 + template_h // 2
        logger.debug(f"框 {i}: 左上角 ({x1}, {y1}), 右下角 ({x2}, {y2}), 中心 ({center_x}, {center_y}), 分数: {scores[i]:.4f}")
    
    boxes = np.array(boxes, dtype=np.int32)
    scores = np.array(scores, dtype=np.float32)
    
    if np.any(np.isnan(scores)) or np.any(np.isinf(scores)):
        logger.error("scores 包含 NaN 或 Inf")
        return [], []
    
    # 按分数降序排序
    indices = np.argsort(scores)[::-1]
    sorted_locations = [locations[i] for i in indices]
    sorted_scores = scores[indices]
    sorted_boxes = boxes[indices]
    
    # 记录排序后的框
    logger.debug("排序后框（按分数降序）:")
    for i, (box, score) in enumerate(zip(sorted_boxes, sorted_scores)):
        center_x = box[0] + template_w // 2
        center_y = box[1] + template_h // 2
        logger.debug(f"排序框 {i}: 左上角 ({box[0]}, {box[1]}), 右下角 ({box[2]}, {box[3]}), 中心 ({center_x}, {center_y}), 分数: {score:.4f}")
    
    # 简化的 NMS：单遍遍历
    keep_indices = []
    for i in range(len(sorted_boxes)):
        current_box = sorted_boxes[i]
        current_score = sorted_scores[i]
        keep = True
        # 检查当前框是否与已保留框重叠
        for kept_idx in keep_indices:
            kept_box = boxes[kept_idx]
            iou = calculate_iou(current_box, kept_box)
            logger.debug(f"框 {indices[i]}（中心: ({current_box[0] + template_w // 2}, {current_box[1] + template_h // 2})）与保留框 {kept_idx} 的 IoU: {iou:.4f}")
            if iou > iou_threshold:
                keep = False
                break
        if keep:
            keep_indices.append(indices[i])
            logger.debug(f"保留框 {indices[i]}: 中心坐标 ({current_box[0] + template_w // 2}, {current_box[1] + template_h // 2}), 分数: {current_score:.4f}")
    
    filtered_locations = [locations[i] for i in keep_indices]
    filtered_scores = [scores[i] for i in keep_indices]
    logger.debug(f"自定义 NMS 后保留 {len(filtered_locations)} 个匹配位置")
    
    # 记录过滤的框
    filtered_indices = set(keep_indices)
    for i in range(len(locations)):
        if i not in filtered_indices:
            center_x = locations[i][0] + template_w // 2
            center_y = locations[i][1] + template_h // 2
            logger.debug(f"过滤框 {i}: 中心坐标 ({center_x}, {center_y}), 分数: {scores[i]:.4f}")
    
    # 保存输入和输出到文件
    debug_path = "wxpuppet/cache/nms_debug.txt"
    with open(debug_path, "w", encoding="utf-8") as f:
        f.write("NMS 输入:\n")
        for i, (box, score) in enumerate(zip(boxes, scores)):
            center_x = box[0] + template_w // 2
            center_y = box[1] + template_h // 2
            f.write(f"框 {i}: 左上角 ({box[0]}, {box[1]}), 右下角 ({box[2]}, {box[3]}), 中心 ({center_x}, {center_y}), 分数: {score:.4f}\n")
        f.write("\nNMS 输出:\n")
        for i, (loc, score) in enumerate(zip(filtered_locations, filtered_scores)):
            center_x = loc[0] + template_w // 2
            center_y = loc[1] + template_h // 2
            f.write(f"保留框 {i}: 中心坐标 ({center_x}, {center_y}), 分数: {score:.4f}\n")
        f.write("\n被过滤框:\n")
        for i in range(len(locations)):
            if i not in filtered_indices:
                center_x = locations[i][0] + template_w // 2
                center_y = locations[i][1] + template_h // 2
                f.write(f"过滤框 {i}: 中心坐标 ({center_x}, {center_y}), 分数: {scores[i]:.4f}\n")
    logger.debug(f"NMS 输入和输出已保存至: {debug_path}")
    
    return filtered_locations, filtered_scores
    
def find_multi_ui_element(template_path, threshold=0.9, ignore_region=None):
    logger.debug("开始执行 find_multi_ui_element 函数")
    left, top, right, bottom = get_wx_window.read_window_position()
    if not all(isinstance(x, int) for x in [left, top, right, bottom]) or right <= left or bottom <= top:
        logger.error(f"无效的窗口位置: 左上角 ({left}, {top}), 右下角 ({right}, {bottom})")
        return None
    
    region = (left, top, right-left, bottom-top)
    screenshot = capture_screenshot(region)
    
    # 检查模板图像是否存在
    if not os.path.exists(template_path):
        logger.error(f"模板图像 {template_path} 不存在")
        return None
    
    # 加载模板图像
    logger.debug(f"加载模板图像: {template_path}")
    template = cv2.imread(template_path, 0)
    if template is None:
        logger.error(f"无法加载模板图像 {template_path}")
        return None
    
    # 记录模板图像尺寸
    template_h, template_w = template.shape
    logger.debug(f"模板图像尺寸: {template_w}x{template_h}")
    
    # 创建掩码
    mask = create_mask(template, ignore_region)
    
    # 检查截图是否有效
    if screenshot is None or not isinstance(screenshot, np.ndarray):
        logger.error("截图为空或无效")
        return None
    
    # 记录截图尺寸
    screenshot_h, screenshot_w = screenshot.shape[:2]
    logger.debug(f"截图尺寸: {screenshot_w}x{screenshot_h}")
    
    # 检查模板和截图尺寸兼容性
    if template_w > screenshot_w or template_h > screenshot_h:
        logger.error(f"模板尺寸 ({template_w}x{template_h}) 大于截图尺寸 ({screenshot_w}x{screenshot_h})")
        return None
    
    # 转换为灰度图
    logger.debug("将截图转换为灰度图")
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    
    # 执行模板匹配
    logger.debug("执行模板匹配 (方法: TM_CCOEFF_NORMED)")
    try:
        result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED, mask=mask)
        logger.debug(f"模板匹配结果形状: {result.shape}")
    except Exception as e:
        logger.error(f"模板匹配失败: {str(e)}")
        return None
    
    # 查找所有满足阈值的匹配位置
    # 过滤 NaN 和 inf 异常值
    valid_mask = np.isfinite(result) & (result >= threshold)

    # 获取有效位置和分数（变量名保持不变）
    locations = np.where(valid_mask)
    locations = list(zip(*locations[::-1]))
    scores = result[valid_mask]

    # 记录日志
    logger.debug(f"初始找到 {len(locations)} 个有效匹配位置")
    
    if not locations:
        logger.warning(f"匹配失败，无位置满足阈值 {threshold}")
        output_path = "wxpuppet/cache/failed_screenshot.png"
        cv2.imwrite(output_path, screenshot)
        logger.info(f"未匹配成功的截图已保存至: {output_path}")
        return None
    logger.debug(f"Scores： {scores} Locations: {locations}")
    # 应用非极大值抑制
    locations, scores = non_max_suppression(locations, scores, template_w, template_h, iou_threshold=0.5)
    if not locations:
        logger.warning("NMS 后无匹配位置")
        output_path = "wxpuppet/cache/failed_screenshot.png"
        cv2.imwrite(output_path, screenshot)
        logger.info(f"未匹配成功的截图已保存至: {output_path}")
        return None
    
    # 计算所有匹配目标的中心坐标
    matches = []
    screenshot_with_box = screenshot.copy()
    for loc in locations:
        top_left = loc
        center_x = top_left[0] + template_w // 2
        center_y = top_left[1] + template_h // 2
        matches.append((center_x, center_y))
        logger.debug(f"匹配位置中心坐标: ({center_x}, {center_y})")
        
        # 可视化匹配结果
        bottom_right = (top_left[0] + template_w, top_left[1] + template_h)
        cv2.rectangle(screenshot_with_box, top_left, bottom_right, (0, 255, 0), 2)
        cv2.circle(screenshot_with_box, (center_x - left, center_y - top), 5, (0, 0, 255), -1)
    
    # 保存可视化结果
    output_path = "wxpuppet/cache/match_result.png"
    cv2.imwrite(output_path, screenshot_with_box)
    logger.info(f"匹配结果（{len(matches)} 个目标）已保存至: {output_path}")
    
    return matches if matches else None


# 唯一目标匹配，返回单个坐标
def find_uni_ui_element(template_path, threshold=0.8):
    logger.debug("开始执行 find_uni_ui_element 函数")
    left, top, right, bottom = get_wx_window.read_window_position()
    region = (left, top, right-left, bottom-top)
    screenshot = capture_screenshot(region)  # 可传入 region=(left, top, width, height)
    
    # 检查模板图像是否存在
    if not os.path.exists(template_path):
        logger.error(f"模板图像 {template_path} 不存在")
        return None
    
    # 加载模板图像
    template = cv2.imread(template_path, 0)
    if template is None:
        logger.error(f"无法加载模板图像 {template_path}")
        return None
    
    # 记录模板图像尺寸
    template_h, template_w = template.shape
    
    # 检查截图是否有效
    if screenshot is None:
        logger.error("截图为空")
        return None
    
    # 记录截图尺寸
    screenshot_h, screenshot_w = screenshot.shape[:2]
    logger.debug(f"截图尺寸: {screenshot_w}x{screenshot_h}")
    
    # 转换为灰度图
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    
    # 执行模板匹配
    result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
    
    # 找到所有大于阈值的匹配位置
    locations = np.where(result >= threshold)
    locations = list(zip(*locations[::-1]))  # 转换为 (x, y) 坐标列表
    
    if not locations:
        logger.warning(f"匹配失败，置信度低于阈值 {threshold}")
        # 保存原始截图以供调试
        output_path = "wxpuppet/cache/failed_screenshot.png"
        cv2.imwrite(output_path, screenshot)
        logger.info(f"未匹配成功的截图已保存至: {output_path}")
        return None
    
    # 找到最右下角的匹配点 (x+y 最大)
    max_sum = -1
    selected_loc = None
    for loc in locations:
        x, y = loc
        if x + y > max_sum:
            max_sum = x + y
            selected_loc = loc
    
    logger.info(f"匹配成功，置信度: {result[selected_loc[1], selected_loc[0]]:.4f} (阈值: {threshold})")
    top_left = selected_loc
    center_x = top_left[0] + template_w // 2
    center_y = top_left[1] + template_h // 2
    logger.debug(f"最右下角匹配中心坐标: ({center_x}, {center_y})")
    
    # 可视化匹配结果
    logger.debug("生成匹配结果可视化图像")
    screenshot_with_box = screenshot.copy()
    bottom_right = (top_left[0] + template_w, top_left[1] + template_h)
    cv2.rectangle(screenshot_with_box, top_left, bottom_right, (0, 255, 0), 2)
    cv2.circle(screenshot_with_box, (center_x, center_y), 5, (0, 0, 255), -1)
    
    # 保存可视化结果
    output_path = "wxpuppet/cache/match_result.png"
    cv2.imwrite(output_path, screenshot_with_box)
    logger.info(f"匹配结果已保存至: {output_path}")
    
    return center_x, center_y

def find_miniprogram_element():
    template_path = "wxpuppet/template/miniprogram.png"
    return  find_ui_element(template_path)

def find_first_search():
    template_path = "wxpuppet/template/first_search.png"
    return  find_ui_element(template_path)

def find_first_self():
    template_path = "wxpuppet/template/first_self.png"
    return  find_ui_element(template_path)

def find_input_box():
    template_path = "wxpuppet/template/input_box.png"
    return  find_ui_element(template_path)

def find_input_send_button():
    template_path = "wxpuppet/template/input_send_button.png"
    return  find_ui_element(template_path)


def find_forward_button_element():
    template_path = "wxpuppet/template/forward_button.png"
    return  find_ui_element(template_path)

def find_search_group_button_element():
    template_path = "wxpuppet/template/search_group.png"
    return  find_ui_element(template_path)

def find_send_msg_element():
    template_path = "wxpuppet/template/send_msg.png"
    return  find_ui_element(template_path)

def find_send_button_element():
    template_path = "wxpuppet/template/send_button.png"
    return  find_ui_element(template_path)

def find_cancel_button_element():
    template_path = "wxpuppet/template/cancel_button.png"
    return  find_ui_element(template_path)

def find_final_send_element():
    template_path = "wxpuppet/template/final_send.png"
    return  find_ui_element(template_path)

def find_show_all_group_element():
    template_path = "wxpuppet/template/show_all_group.png"
    return  find_ui_element(template_path)

def find_multi_group_button_element():
    template_path = "wxpuppet/template/multi_group.png"
    return  find_multi_ui_element(template_path,ignore_region=(30, 0, 55, 45))

def find_multi_group_test_button_element():
    template_path = "wxpuppet/template/multi_group_test.png"
    return  find_multi_ui_element(template_path,ignore_region=(40, 0, 40, 45))


def find_uni_sended_msg_element():
    template_path = "wxpuppet/template/sended_msg.png"
    return  find_uni_ui_element(template_path)


def capture_screenshot(region=None):
    """捕获屏幕截图"""
    logger.debug("开始捕获屏幕截图")
    time.sleep(0.5)  # 给用户时间准备
    screenshot = pyautogui.screenshot(region=region)
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    logger.debug("截图捕获完成")
    return screenshot

if __name__ == "__main__":
    time.sleep(3)
    find_multi_group_button_element() 

