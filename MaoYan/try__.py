import os
import cv2
import pyttsx3 as pyt
import imageio
import numpy as np
from PIL import ImageFont

# with open('woff_img\eb54399b\images\eedf.png','rb') as f:
#     i1 = f.read()
#
# with open("woff_img\img/2.png",'rb') as f:
#     img = f.read()
#
# if i1 == img:
#     print("相同")
# else:
#     print("不同")

# 模版匹配
templates = os.listdir('woff_img\img/')

for i in range(len(templates)):
    templates[i] = "woff_img/img/" + templates[i]

images = os.listdir('woff_img/eb54399b/images/')

images_path = []
for i in range(len(images)):
    images_path[i] = "woff_img/img/" + images[i]
    images[i] = images[i].replace(".png", "")

print(images, templates, images_path)


# 读取一个模板地址与图片进行匹配，返回得分
def template_score(template, image):
    # 将模板进行格式转换
    template_img = cv2.imdecode(np.fromfile(template, dtype=np.uint8), 1)
    ret, template_img = cv2.threshold(template_img, 0, 255, cv2.THRESH_OTSU)
    image_ = image.copy()
    result = cv2.matchTemplate(image_, template_img, cv2.TM_CCOEFF)
    return result[0][0]


# 对字符逐一匹配
def template_matching(word_images):
    results = {}
    for index, word_image in enumerate(word_images):
        best_score = []
        score = []
        for template in templates:
            result = template_score(template, word_image)
            score.append(result)
        i = score.index(max(score))
        results[str(i)]=images[index]
    return results

img = cv2.imread('woff_img\eb54399b\images\eedf.png')
result = template_matching(word_images_)
print(result)
# "".join(result)函数将列表转换为拼接好的字符串，方便结果显示
print("".join(result))
