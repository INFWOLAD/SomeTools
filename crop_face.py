import os
import cv2
from facenet_pytorch import MTCNN
from PIL import Image
from tqdm import tqdm
import numpy as np


def get_boundingbox(face, width, height, scale=1.3, minsize=None):
    """
    Expects a dlib face to generate a quadratic bounding box.
    :param face: dlib face class
    :param width: frame width
    :param height: frame height
    :param scale: bounding box size multiplier to get a bigger face region
    :param minsize: set minimum bounding box size
    :return: x, y, bounding_box_size in opencv form
    """
    x1 = face[0]
    y1 = face[1]
    x2 = face[2]
    y2 = face[3]
    size_bb = int(max(x2 - x1, y2 - y1) * scale)
    if minsize:
        if size_bb < minsize:
            size_bb = minsize
    center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2

    # Check for out of bounds, x-y top left corner
    x1 = max(int(center_x - size_bb // 2), 0)
    y1 = max(int(center_y - size_bb // 2), 0)
    # Check for too big bb size for given x, y
    size_bb = min(width - x1, size_bb)
    size_bb = min(height - y1, size_bb)

    return x1, y1, size_bb


def get_face(videoPath, save_root, select_nums=10):
    numFrame = 0
    v_cap = cv2.VideoCapture(videoPath)
    v_len = int(v_cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 7代表读取视频文件的帧数
    if v_len > select_nums:
        samples = np.linspace(0, v_len - 1, 10).round().astype(int)  # linespace创建等差数列
    else:
        samples = np.linspace(0, v_len - 1, v_len).round().astype(int)
    for j in range(v_len):
        success, vframe = v_cap.read()
        # 按帧读取视频，ret,frame是获cap.read()方法的两个返回值。其中ret是布尔值，如果读取帧是正确的则返回True，如果文件读取到结尾，它的返回值就为False。frame就是每一帧的图像，是个三维矩阵。
        if j in samples:
            height, width = vframe.shape[:2]
            image = cv2.cvtColor(vframe, cv2.COLOR_BGR2RGB)  # 这里只是表示一个通道的转换，例如：如果你用cv2读取了一幅图片，读进去的是BGR格式的，但是在保存图片时，要保存为RGB格式的
            image = Image.fromarray(image)

            try:
                boxes, _ = mtcnn.detect(image)  # 监测所有人脸
                x, y, size = get_boundingbox(boxes.flatten(), width, height)
                cropped_face = vframe[y:y + size, x:x + size]

                s = str(numFrame)
                if not os.path.exists(save_root):
                    os.makedirs(save_root)
                cv2.imwrite(os.path.join(save_root, "%s.png") % s, cropped_face)
                numFrame += 1

            except:
                print(videoPath)
    v_cap.release()


if __name__ == '__main__':
    # Modify the following directories to yourselves
    VIDEO_ROOT = 'D:\Tools\Program\Celeb-DF-v2'          # The base dir of CelebDF-v2 dataset
    OUTPUT_PATH = 'D:\Tools\Program\Celeb-DF-v2-crop/'    # Where to save cropped training faces
    TXT_PATH = "./train-list.txt"    # the given train-list.txt file

    with open(TXT_PATH, "r") as f:
        data = f.readlines()

    # Face detector
    mtcnn = MTCNN(device='cuda:0').eval()
    for line in data:
        video_name = line[2:-1]
        video_path = os.path.join(VIDEO_ROOT, video_name)
        save_dir = OUTPUT_PATH + video_name.split('.')[0]
        get_face(video_path, save_dir)
