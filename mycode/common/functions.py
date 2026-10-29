"""激活函数与损失函数。"""

import numpy as np


def sigmoid(x):
    """逐元素计算 sigmoid 激活函数。"""
    x = np.asarray(x)
    return 1 / (1 + np.exp(-x))


def softmax(x):
    """将分数转换成概率；二维输入的每一行对应一个样本。"""
    x = np.asarray(x)
    exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return exp_x / np.sum(exp_x, axis=-1, keepdims=True)


def cross_entropy_error(y, t):
    """计算平均交叉熵，标签支持类别编号或 one-hot 编码。"""
    y = np.asarray(y)
    t = np.asarray(t)
    if y.ndim == 1:
        y = y.reshape(1, -1)

    batch_size = y.shape[0]
    if t.size == y.size:
        t = t.reshape(y.shape).argmax(axis=1)
    else:
        t = t.reshape(-1)

    return -np.mean(np.log(y[np.arange(batch_size), t] + 1e-7))
