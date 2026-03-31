# 对src、trg的路径做了修改

import xml.etree.ElementTree as ET
import os
from os import getcwd
from tqdm import tqdm
import shutil

classes = ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"]

def convert(size, box):
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)

def convert_annotation(in_file, out_file):
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    with open(out_file, 'w') as f:
        for obj in root.iter('object'):
            difficult = obj.find('difficult').text
            cls = obj.find('name').text
            if cls not in classes or int(difficult) == 1:
                continue
            cls_id = classes.index(cls)
            xmlbox = obj.find('bndbox')
            b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text),
                 float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
            bb = convert((w, h), b)
            f.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')

def convert_dataset(src_dir, dst_dir):
    """
    将VOC格式数据集转换为YOLO格式并保存到指定目录。
    
    src_dir: 原始数据集路径，其下包含 ANNOTATIONS/ 和 IMAGES/ 两个文件夹
    dst_dir: 目标保存路径，数据集名称保持不变
    """
    # 获取数据集名称（最后一级目录名）
    dataset_name = os.path.basename(os.path.normpath(src_dir))

    # 原始路径
    src_annotations = os.path.join(src_dir, 'ANNOTATIONS')
    src_images = os.path.join(src_dir, 'IMAGES')

    # 目标路径：保持数据集名称不变
    dst_dataset = os.path.join(dst_dir, dataset_name)
    dst_labels = os.path.join(dst_dataset, 'labels')
    dst_images = os.path.join(dst_dataset, 'images')

    os.makedirs(dst_labels, exist_ok=True)
    os.makedirs(dst_images, exist_ok=True)

    # 1. 转换标注：XML -> YOLO TXT
    xml_files = [f for f in os.listdir(src_annotations) if f.endswith('.xml')]
    print(f"共找到 {len(xml_files)} 个标注文件，开始转换...")
    for xml_file in tqdm(xml_files, desc="转换标注"):
        image_id = os.path.splitext(xml_file)[0]
        in_file = os.path.join(src_annotations, xml_file)
        out_file = os.path.join(dst_labels, image_id + '.txt')
        convert_annotation(in_file, out_file)

    # 2. 复制图片到目标目录
    img_files = os.listdir(src_images)
    print(f"共找到 {len(img_files)} 张图片，开始复制...")
    for img_file in tqdm(img_files, desc="复制图片"):
        src_path = os.path.join(src_images, img_file)
        dst_path = os.path.join(dst_images, img_file)
        shutil.copy2(src_path, dst_path)

    print(f"\n转换完成！新数据集保存在: {dst_dataset}")
    print(f"  标签目录: {dst_labels}")
    print(f"  图片目录: {dst_images}")

if __name__ == "__main__":
    src_dir = 'data/defect/NEU-DET'   # 原始数据集路径
    dst_dir = 'code/DefectDet/datasets'      # 目标保存路径

    convert_dataset(src_dir, dst_dir)