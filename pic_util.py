import math
import os
import json
from io import BytesIO
import base64
import string

current_path = os.path.abspath(__file__)

directory = os.path.dirname(current_path)
res_dir = directory + "/resources/"
yuanshen_ttf = res_dir + "yuanshen.ttf"
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Optional, Tuple, Union, List

def add_colored_text_to_image(image: Union[Image.Image, str], text: str, start_coord: Tuple[int, int],
                              end_coord: Tuple[int, int], text_size: int, font_path: str,alignment: Tuple[int, int] = (1,1),
                              color_mapping: Optional[Dict[str, Tuple[int, int, int]]] = {},
                              default_color: Tuple[int, int, int] = (0, 0, 0),
                              output_path: Optional[str] = None):
    """
    在图像中添加着色的文本。

    参数:
    image (Union[Image.Image, str]): 输入图像实例或图像文件的路径。
    text (str): 要添加的文本。
    start_coord (Tuple[int, int]): 文本框左上角的坐标 (x, y)。
    end_coord (Tuple[int, int]): 文本框右下角的坐标 (x, y)。
    text_size (int): 文本的字体大小。
    font_path (str): 字体文件的路径。
    text_color (Tuple[int, int, int], optional): 默认文本颜色 (R, G, B)。
    color_mapping (Dict[str, Tuple[int, int, int]], optional): 文本颜色映射的字典，格式为 {"子串": (R, G, B)}。
    default_color (Tuple[int, int, int], optional): 未映射到颜色的文本使用的默认颜色 (R, G, B)。
    output_path (str, optional): 输出图像的路径。
    alignment (Tuple[int, int]): 文本框的对齐选项，值为 (horizontal_alignment, vertical_alignment)。
                                horizontal_alignment: 0 表示居左，1 表示居中，2 表示居右。
                                vertical_alignment: 0 表示居上，1 表示居中，2 表示居下。
    返回:
    Image.Image: 添加文本后的图像对象。

    示例:
    text_color_mapping = {
        "ab": (255, 0, 0),   # 红色
        "b": (0, 255, 0),   # 绿色
    }
    add_colored_text_to_image("input.jpg", "abbb\nababbbaab123", (100, 100), (500, 150), 20, "font.ttf",
                              text_color=(255, 255, 255), color_mapping=text_color_mapping,
                              default_color=(0, 0, 0), output_path="output.jpg").show()
    """

    if isinstance(image, str):
        image = Image.open(image)

    text_box_width = end_coord[0] - start_coord[0]
    text_box_height = end_coord[1] - start_coord[1]
    text_box_center = (start_coord[0] + text_box_width // 2, start_coord[1] + text_box_height // 2)

    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, size=text_size)
    char_width, char_height = draw.textsize("A", font=font)

    text = preprocess_text(text, text_box_width, font)
    lines = text.split('\n')

    text_height = len(lines) * char_height
    if len(lines) >= 1:
        text_width, text_height = draw.textsize(text, font=font)
        if alignment[0] == 0:  # Left alignment
            text_start = (start_coord[0], text_box_center[1] - text_height // 2)
        elif alignment[0] == 1:  # Center alignment
            text_start = (text_box_center[0] - text_width // 2, text_box_center[1] - text_height // 2)
        else:  # Right alignment
            text_start = (end_coord[0] - text_width, text_box_center[1] - text_height // 2)
    else:
        if alignment[0] == 0:  # Left alignment
            text_start = (start_coord[0], text_box_center[1] - text_height // 2)
        elif alignment[0] == 1:  # Center alignment
            text_start = (text_box_center[0] - text_box_width // 2, text_box_center[1] - text_height // 2)
        else:  # Right alignment
            text_start = (end_coord[0] - text_box_width, text_box_center[1] - text_height // 2)

    if alignment[1] == 0:  # Top alignment
        y_position = start_coord[1]
    elif alignment[1] == 1:  # Center alignment
        y_position = text_box_center[1] - text_height // 2
    else:  # Bottom alignment
        y_position = end_coord[1] - text_height
    
    for line in lines:
        x_position = text_start[0]
        index = 0
        while index < len(line):
            found_color_mapping = False
            for key in color_mapping.keys():
                if line[index:index+len(key)] == key:
                    draw.text((x_position, y_position), key, font=font, fill=color_mapping[key])
                    x_position += calculate_text_width(key, font)  # 添加间距
                    index += len(key)
                    found_color_mapping = True
                    break

            if not found_color_mapping:
                char = line[index]
                char_width = calculate_text_width(char, font)
                draw.text((x_position, y_position), char, font=font, fill=default_color)
                x_position += char_width  # 添加间距
                index += 1

        y_position += char_height

    if output_path:
        image.save(output_path)

    return image

def calculate_text_width(text, font):
    char_widths = [font.getsize(char)[0] for char in text]
    total_width = sum(char_widths)
    return total_width

def preprocess_text(text, max_width, font):
    lines = []
    current_line = ""
    for char in text:
        if char == "\n":
            lines.append(current_line)
            current_line = ""
        else:
            if calculate_text_width(current_line + char, font) <= max_width:
                current_line += char
            else:
                lines.append(current_line)
                current_line = char
    if current_line:
        lines.append(current_line)
    return "\n".join(lines)  # 将行列表拼接为字符串

def paste_image(image: Image.Image, paste_image: Image.Image, start_coord: Tuple[int, int], end_coord: Tuple[int, int],
                size_ratio: float, opacity: float):
    """
    在图像上粘贴另一张图像。

    参数:
    image (Image.Image): 目标图像实例。
    paste_image (Image.Image): 要粘贴的图像实例。
    start_coord (Tuple[int, int]): 粘贴区域左上角的坐标 (x, y)。
    end_coord (Tuple[int, int]): 粘贴区域右下角的坐标 (x, y)。
    size_ratio (float): 粘贴图像的大小比例。
    opacity (float): 粘贴图像的透明度，范围从 0（完全透明）到 1（不透明）。

    返回:
    Image.Image: 完成粘贴操作后的图像实例。

    示例:
    target_image = Image.open("target_image.jpg")
    paste_image = Image.open("paste_image.png")
    result_image = paste_image(target_image, paste_image, (100, 100), (300, 200), 0.5, 0.8)
    result_image.show()
    """
    # 计算粘贴区域的中心坐标
    paste_box_width = end_coord[0] - start_coord[0]
    paste_box_height = end_coord[1] - start_coord[1]
    paste_box_center = (start_coord[0] + paste_box_width // 2, start_coord[1] + paste_box_height // 2)

    # 计算粘贴图片的大小
    paste_width = int(paste_box_width * size_ratio)
    paste_height = int(paste_box_height * size_ratio)

    # 根据宽度或高度的最大比例进行调整
    max_ratio = max(paste_width / paste_image.width, paste_height / paste_image.height)
    paste_size = (int(paste_image.width * max_ratio), int(paste_image.height * max_ratio))
    paste_image = paste_image.resize(paste_size)

    # 设置透明度
    paste_image = paste_image.convert("RGBA")
    paste_image = paste_image.point(lambda p: p * opacity)

    # 计算粘贴图片的起始坐标
    paste_start = (paste_box_center[0] - paste_size[0] // 2, paste_box_center[1] - paste_size[1] // 2)

    # 在图像上粘贴透明图片
    image.paste(paste_image, paste_start, mask=paste_image)

    return image



def apply_transparent_mask(image: Image.Image, transparent_color: tuple, position_ranges: List[tuple]=None):
    """
    给图片指定位置范围添加透明颜色遮罩。
    
    参数：
    image (str 或 Image.Image): 图片路径或者Image实例。
    transparent_color (tuple): 透明颜色，使用RGBA格式。
    position_ranges (list): 位置范围列表，每个范围包含起始坐标和终止坐标，如 [(x1, y1, x2, y2), ...]。
    
    返回：
    Image.Image: 处理后的Image实例。
    """
    if isinstance(image, str):
        img = Image.open(image)
    elif isinstance(image, Image.Image):
        img = image
    else:
        raise ValueError("image 参数必须是图片路径或者Image实例。")
    
    mask = Image.new("RGBA", img.size, (0, 0, 0, 0))
    
    draw = ImageDraw.Draw(mask)
    draw.rectangle((0, 0, img.width, img.height), fill=transparent_color)
    
    if position_ranges:
        for start_x, start_y, end_x, end_y in position_ranges:
            mask_region = Image.new("RGBA", img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(mask_region)
            draw.rectangle((start_x, start_y, end_x, end_y), fill=transparent_color)
            img.paste(mask_region, (0, 0), mask_region)
    else:
        img.paste(mask, (0, 0), mask)
    
    return img

def append_images(image1: Union[str, Image.Image],
                  image2: Union[str, Image.Image],
                  direction: int,
                  padding_direction: int,
                  fill_color: Tuple[int, int, int, int] = (255, 255, 255, 0)):
    """
    在指定方向上追加两张图片。

    参数:
        image1 (Union[str, Image.Image]): 第一张图片（可以是路径或图片对象）。
        image2 (Union[str, Image.Image]): 第二张图片（可以是路径或图片对象）。
        direction (int): 追加图片的方向（0 表示横向，1 表示纵向）。
        padding_direction (int): 设置填充边距的方向（0 或 1）。
        fill_color (Tuple[int, int, int, int]): 用于填充空白区域的颜色（默认为透明）。

    返回:
        Image.Image: 追加后的结果图片。
    """
    if isinstance(image1, str):
        image1 = Image.open(image1)
    if isinstance(image2, str):
        image2 = Image.open(image2)

    width1, height1 = image1.size
    width2, height2 = image2.size

    if direction == 0:
        new_width = width1 + width2
        new_height = max(height1, height2)
    elif direction == 1:
        new_width = max(width1, width2)
        new_height = height1 + height2
    else:
        raise ValueError("无效的方向。请使用 0 表示横向，1 表示纵向。")

    new_image = Image.new('RGBA', (new_width, new_height), fill_color)

    if direction == 0:
        if padding_direction == 0:

            new_image.paste(image1, (0, 0))
            new_image.paste(image2, (width1, 0))

        elif padding_direction == 1:
            new_image.paste(image1, (0, new_height - height1))
            new_image.paste(image2, (width1, new_height - height2))
    elif direction == 1:
        if padding_direction == 0:
            new_image.paste(image1, (0, 0))
            new_image.paste(image2, (0, height1))
        elif padding_direction == 1:
            new_image.paste(image1, (new_width - width1, 0))
            new_image.paste(image2, (new_width - width2, height1))

    return new_image


def rotate_image(image: Image.Image, angle_degrees: float):
    """
    旋转图像。

    参数:
        image (Image.Image): 要旋转的 PIL 图像对象。
        angle_degrees (float): 旋转角度（以度为单位）。

    返回:
        Image.Image: 旋转后的 PIL 图像对象。
    """
    # Convert angle from degrees to radians
    angle_radians = math.radians(angle_degrees)
    
    # Rotate the image
    rotated_image = image.rotate(angle_degrees, expand=True)
    
    return rotated_image

def render_progress_bar(completed: float, total: float, width: int = 200, height: int = 20,
                        bar_color: Tuple[int, int, int] = (0, 255, 0),
                        background_color: Tuple[int, int, int] = (255, 255, 255),
                        corner_radius: int = 10):
    """
    渲染一个带有圆角的进度条图像。

    参数:
        completed (float): 已完成的进度部分（例如，70 表示完成了 70%）。
        total (float): 表示完成的总值（例如，100 表示完成了 100%）。
        width (int, optional): 进度条图像的宽度。默认为 200。
        height (int, optional): 进度条图像的高度。默认为 20。
        bar_color (Tuple[int, int, int], optional): 进度条的颜色。默认为 (0, 255, 0)。
        background_color (Tuple[int, int, int], optional): 图像的背景颜色。默认为 (255, 255, 255)。
        corner_radius (int, optional): 圆角的半径。默认为 10。

    返回:
        Image.Image: 代表带有圆角的进度条的 PIL 图像对象。
    """
    # Calculate the width of the progress bar based on the completed and total values
    progress_width = int((completed / total) * width)
    
    # Create a new image with the specified dimensions and background color
    image = Image.new("RGBA", (width, height))
    draw = ImageDraw.Draw(image)
    
    # Draw the background of the progress bar with rounded corners
    draw.rounded_rectangle([(0, 0), (width, height)], fill=background_color, radius=corner_radius)
    
    # Draw the completed portion of the progress bar with rounded corners
    draw.rounded_rectangle([(0, 0), (progress_width, height)], fill=bar_color, radius=corner_radius)
    
    return image

def convert_png_to_jpg_with_lower_quality(image: Image.Image, ratio: float, quility: int = 100, save=False):
    """
    将PNG图像转换为JPEG格式并降低质量。

    参数:
    image (Image.Image): 输入的PNG图像实例。
    ratio (float): 缩放比例，新图像尺寸为原图尺寸乘以此比例。

    返回:
    Image.Image: 转换为JPEG格式并降低质量后的图像实例。

    示例:
    png_image = Image.open("input.png")
    jpg_image = convert_png_to_jpg_with_lower_quality(png_image, 0.5)
    jpg_image.save("output.jpg")
    jpg_image.show()
    """
    re_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
    # 将PNG图像转换为RGB模式
    rgb_image = image.convert("RGB")
    
    rgb_image = rgb_image.resize(re_size)
    # 创建新的JPEG图像对象，大小和原图相同
    jpeg_image = Image.new("RGB", re_size)

    # 将RGB图像粘贴到JPEG图像对象中
    jpeg_image.paste(rgb_image, (0, 0))
    rgb_image.close()
    # 降低JPEG图像质量并返回图像对象
    if save:
        jpeg_image.save("result.jpg", quality=quility)
    return jpeg_image



def pic2b64(pic: Image.Image, quality):
    """
    说明:
        PIL图片转base64
    参数:
        :param pic: 通过PIL打开的图片文件
    """
    buf = BytesIO()
    pic.save(buf, format="JPEG", quality=quality)
    base64_str = base64.b64encode(buf.getvalue()).decode()
    return "base64://" + base64_str

