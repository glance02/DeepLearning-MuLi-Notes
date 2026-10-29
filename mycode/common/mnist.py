"""读取本地已下载的 MNIST 数据集。"""

from pathlib import Path

import numpy as np


def load_mnist(normalize=True, flatten=True, one_hot_label=False):
    """返回 (训练图像, 训练标签), (测试图像, 测试标签)。

    normalize：将像素从 0—255 缩放为 0—1 的 float32 数组。
    flatten：展开为长度 784 的向量；否则每张图像形状为 (1, 28, 28)。
    one_hot_label：将类别编号转换为长度 10 的 one-hot 向量。
    """
    # 使用本地现有文件名；路径不依赖调用者的工作目录。
    path = Path(__file__).resolve().parent.parent / "data" / "minist.npz"
    with np.load(path, allow_pickle=False) as data:
        x_train = data["x_train"]
        t_train = data["y_train"]
        x_test = data["x_test"]
        t_test = data["y_test"]

    if normalize:
        x_train = x_train.astype(np.float32) / 255.0
        x_test = x_test.astype(np.float32) / 255.0

    if flatten:
        x_train = x_train.reshape(-1, 784)
        x_test = x_test.reshape(-1, 784)
    else:
        x_train = x_train.reshape(-1, 1, 28, 28)
        x_test = x_test.reshape(-1, 1, 28, 28)

    if one_hot_label:
        table = np.eye(10)
        t_train = table[t_train]
        t_test = table[t_test]

    return (x_train, t_train), (x_test, t_test)
