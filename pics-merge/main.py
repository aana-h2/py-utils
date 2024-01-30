import sys

from PIL import Image
from pathlib import Path
from typing import List


# 先不添加任何的配置功能好了，目前感觉也用不上。

def read_image_list(p='.'):
    path = Path(p)
    if not path.is_dir():
        raise NotADirectoryError('need a directory.')
    image_list = []
    for child in path.iterdir():
        if child.suffix.__str__() in ['.jpg', '.png']:
            image_list.append(Image.open(child.__str__()))
    return image_list


# 按条裁剪。宽度等于图片宽度，高度等于目标高度。
def crop_in_row(height: int, image_list: List[Image.Image]) -> List[Image.Image]:
    cropped_list = []
    for image in image_list:
        w, h = image.size
        crop_height = min(height, h)
        cropped_image = image.crop((0, h - crop_height, w, h))
        cropped_list.append(cropped_image)
    return cropped_list


# 从上到下进行拼接。
# 创建一个空白的图，其长度为所有的片段的和，宽度为所有片段的max。
# 图的底色为黑色。
def merge_rows(image_list: List[Image.Image]) -> Image.Image:
    total_height = 0
    max_width = 0
    for image in image_list:
        w, h = image.size
        max_width = max(max_width, w)
        total_height += h
    background = Image.new('RGB', (max_width, total_height))
    paste_x = 0
    paste_y = 0
    for image in image_list:
        background.paste(image, (paste_x, paste_y))
        paste_y += image.height
    return background


# 参数：
# 1. 保存了图片的目录
# 2. 截取的高度
def main():
    if len(sys.argv) < 3:
        raise AssertionError('need directory and height.')
    image_list = read_image_list(sys.argv[1])
    merged_img = merge_rows(crop_in_row(int(sys.argv[2]), image_list))
    merged_img.save('merged_image.png')


if __name__ == '__main__':
    main()
