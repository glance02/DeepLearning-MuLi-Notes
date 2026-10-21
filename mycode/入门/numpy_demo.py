import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# 生成数d据
x = np.arange(0, 6, 0.1)
y1 = np.sin(x)
y2 = np.cos(x)

# 绘制图形
plt.plot(x, y1, label="sin")
plt.plot(x, y2, linestyle="--", label="cos")
plt.xlabel("x")
plt.ylabel("y")
plt.title("sin & cos")
plt.legend()
plt.show()

# 读入图像
from PIL import Image
import matplotlib.pyplot as plt

img = Image.open('D:/code/github/DeepLearning-MuLi-Notes/mycode/入门/photo.png')
plt.imshow(img)
plt.show()